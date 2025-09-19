import logging
from functools import reduce
from types import ModuleType
from typing import Annotated, Type
from fastapi import FastAPI, Path, HTTPException
from fastapi.routing import APIRoute, APIRouter
from pydantic import BaseModel, ConfigDict

# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.inmemory import InMemoryBackend
from starlette import status
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.types import Lifespan
from tortoise import Tortoise, ModelMeta
from tortoise.contrib.pydantic import PydanticModel
from tortoise.contrib.starlette import register_tortoise
from tortoise.exceptions import IntegrityError, DoesNotExist
from tortoise_api_model.enum import Scope
from tortoise_api_model.model import Model
from tortoise_api_model.pydantic import PydList, Names

from tortoise_api.loader import _repr
from tortoise_api.oauth import OAuth, on_error


class ListArgs(BaseModel):
    model_config = ConfigDict(extra="allow")
    limit: int = 100
    offset: int = 0
    sort: str | None = "-id"
    q: str | None = None


class Api:
    app: FastAPI
    module: ModuleType
    db_url: str
    models: {str: Model}
    oauth: OAuth
    redis = None
    prefix = "/v2"

    def __init__(
        self,
        module: ModuleType,
        db_url: str,
        debug: bool = False,
        title: str = "FemtoAPI",
        exc_models: set[str] = None,
        lifespan: Lifespan = None,
        oauth: OAuth = None,
    ):
        """
        Parameters:
            debug: Debug SQL queries, api requests
            # auth_provider: Authentication Provider
        """
        self.title = title
        if debug:
            self.debug = True
            logging.basicConfig(level=logging.DEBUG)

        # self.module =
        self.set_models(module, exc_models)
        self.db_url = db_url
        self.oauth = oauth

        # get auth token route
        auth_routes = [
            APIRoute(
                "/register",
                self.oauth.reg_user,
                methods=["POST"],
                tags=["auth"],
                name="SignUp",
                response_model=self.oauth.Token,
                operation_id="register",
            ),
            APIRoute(
                "/token",
                self.oauth.login_for_access_token,
                methods=["POST"],
                response_model=self.oauth.Token,
                tags=["auth"],
                operation_id="token",
            ),
        ]

        # main app
        self.app = FastAPI(
            debug=debug, routes=auth_routes, title=title, separate_input_output_schemas=False, lifespan=lifespan
        )
        # CORS # noinspection PyTypeChecker
        self.app.add_middleware(
            CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
        )

        # noinspection PyTypeChecker
        self.app.add_middleware(AuthenticationMiddleware, backend=self.oauth, on_error=on_error)

        # FastAPICache.init(InMemoryBackend(), expire=600)
        # db init
        register_tortoise(self.app, db_url=self.db_url, modules={"models": [self.module]}, generate_schemas=debug)

    def set_models(self, modul, excm: set[str]):
        # extract models from module
        models_trees: {Model.__class__: [Model.__class__]} = {
            mdl: mdl.mro() for key in dir(modul) if isinstance(mdl := getattr(modul, key), Model.__class__)
        }
        # collect not top (bottom) models for removing
        bottom_models: {Model.__class__} = reduce(lambda x, y: x | set(y[1:]), models_trees.values(), {object}) & set(
            models_trees
        )
        # filter only top model names
        mm = {m: v for m in dir(modul) if isinstance(v := getattr(modul, m), ModelMeta)}
        [delattr(modul, n) for n, m in mm.items() if m in bottom_models]
        self.module = modul
        top_models = set(models_trees.keys()) - bottom_models
        # set global models list
        self.models = {m.__name__: m for m in top_models if not excm or m.__name__ not in excm}

    def gen_routes(self):
        Tortoise.init_models([self.module], "models")  # for relations

        schemas: {str: (Type[PydanticModel], Type[PydanticModel], Type[PydList])} = {
            k: (m.pyd(), m.pydIn(), m.pydsList()) for k, m in self.models.items()
        }

        # build routes with schemas
        for name, schema in schemas.items():

            def _req2mod(req: Request) -> Type[Model]:
                nam: str = req.scope["path"].split("/")[2]
                return self.models[nam]

            async def index(request: Request, params: ListArgs) -> schema[2]:
                mod: Model.__class__ = _req2mod(request)
                sorts = [params.sort] if params.sort else mod._sorts
                owner: int | None = request.user.id if Scope.All.name not in request.auth.scopes else None
                data = await mod.pagePyd(sorts, params.limit, params.offset, params.q, owner, **params.model_extra)
                return data

            async def names(
                request: Request,
                fname: str = None,
                fval: int | str | bool = None,
                sname: str = None,
                sid: int = None,
                page: int = 1,
                limit: int = 50,
                search: str = None,
            ) -> Names:
                mod: Model.__class__ = _req2mod(request)
                fltr = {fname: fval} if fname else {}
                query = mod.pageQuery(list(mod._name), q=search, **fltr)
                selected = []
                if sid and sname:
                    if (sname := sname.lower()) in mod._meta.fetch_fields or (
                        sname := sname + "s"
                    ) in mod._meta.fetch_fields:
                        selected = await mod.filter(**{sname: sid}).values_list("id", flat=True)
                rels: list[str] = []
                keys: list[str] = ["id"]
                for nam in mod._name:
                    parts = nam.split("__")
                    if len(parts) > 1:
                        rels.append("__".join(parts[:-1]))
                    keys.append(nam)
                query = query.prefetch_related(*rels)
                filtered = await query.count()
                if "logo" in mod._meta.fields:
                    keys.append("logo")
                if page > 0:
                    query = query.limit(limit).offset(limit * (page - 1))
                data = await query.values(*keys)
                data = [{"text": _repr(d, mod._name), "selected": d["id"] in selected, **d} for d in data]
                return Names(results=data, pagination=Names.Pagination(more=filtered > limit * page))

            async def one(request: Request, item_id: Annotated[int, Path()]) -> schema[0]:
                mod = _req2mod(request)
                owner: int | None = Scope.All.name not in request.auth.scopes and request.user.id
                try:
                    return await mod.one(item_id, owner)  # show one
                except DoesNotExist:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            async def upsert(obj: schema[1], item_id: int | None = None) -> schema[0]:
                mod: Type[Model] = obj.model_config["orig_model"]
                obj_dict = obj.model_dump()
                args = [obj_dict]
                if item_id:
                    args.append(item_id)
                try:
                    obj_db: Model = await mod.upsert(*args)
                except IntegrityError as e:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.__repr__())
                # pyd: PydanticModel = await mod.pyd().from_tortoise_orm(obj_db)
                pyd = await mod.one(obj_db.id)  # todo: double request, dirty fix for buildint in topli with recursion=2
                return pyd

            async def delete(req: Request, item_id: int):
                mod = _req2mod(req)
                try:
                    # noinspection PyUnresolvedReferences
                    r = await mod.get(id=item_id).delete()
                    return {"deleted": r}
                except Exception as e:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.__repr__())

            perms: tuple[bool, bool, bool] = schema[0].model_config["orig_model"]._permissions
            upd_perm = (
                tmp
                if (tmp := list({self.oauth.write if perms[1] else None, self.oauth.my if perms[2] else None}))[0]
                else None
            )
            ar = APIRouter(
                routes=[
                    # todo: add "my" endpoints with rules
                    APIRoute(
                        "/" + name,
                        index,
                        methods=["POST"],
                        name=name + " objects list",
                        dependencies=[self.oauth.read] if perms[0] else None,
                        response_model=schema[2],
                        operation_id=f"get{name}List",
                    ),
                    APIRoute(
                        "/" + name,
                        names,
                        methods=["GET"],
                        name=name + " names list",
                        response_model=Names,
                        operation_id=f"get{name}NamesList",
                    ),
                    APIRoute(
                        "/" + name,
                        upsert,
                        methods=["PUT"],
                        name=name + " object create",
                        dependencies=[self.oauth.write] if perms[1] else None,
                        response_model=schema[0],
                        operation_id=f"new{name}",
                    ),
                    APIRoute(
                        "/" + name + "/{item_id}",
                        one,
                        methods=["GET"],
                        name=name + " object get",
                        dependencies=[self.oauth.read] if perms[2] else None,
                        response_model=schema[0],
                        operation_id=f"get{name}",
                    ),
                    APIRoute(
                        "/" + name + "/{item_id}",
                        upsert,
                        methods=["PATCH"],
                        name=name + " object update",
                        dependencies=upd_perm,
                        response_model=schema[0],
                        operation_id=f"upd{name}",
                    ),
                    APIRoute(
                        "/" + name + "/{item_id}",
                        delete,
                        methods=["DELETE"],
                        name=name + " object delete",
                        dependencies=upd_perm,
                        response_model=dict,
                        operation_id=f"del{name}",
                    ),
                ]
            )
            self.app.include_router(
                ar,
                prefix=self.prefix,
                tags=[name],
                dependencies=[self.oauth.active] if perms[0] and perms[1] and perms[2] else None,
            )
