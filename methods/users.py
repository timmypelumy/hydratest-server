﻿from jsonrpcserver import method, JsonRpcError, Error, InvalidParams, Success
from models.users import CreateUserModel,LoginDataModel,RefreshTokenModel
from lib.utils import model_validate, generate_user_id, hash_password, verify_password, jwt_encode, jwt_decode
from lib.db import redis_db
from models.settings import Settings
from time import time
from lib.utils import authenticate_user, validate_req


settings = Settings()




@method( name = "users.create")
async def create_user(  req : CreateUserModel ):
    err,  model =  model_validate( CreateUserModel, req)

    if err:
        return InvalidParams(err)


    id = "U" + generate_user_id()
    password_hash = hash_password(model.password, id)

    data = model.dict(exclude = {'password',})

    data.update({
        'id' : id,
        'password_hash' : password_hash
    })


    redis_db.json().arrappend( "users", "$",  data )

    response = model.dict(by_alias = True, exclude= {'password',})
    response.update( { "id" : id})


    return Success({
        "ok" : True,
        "data" : response
    })




@method( name = "users.refresh_token")
async def refresh_token( req : RefreshTokenModel ):

    err,  model =  model_validate( RefreshTokenModel, req)

    if err:
        return InvalidParams(err)

    err, payload = jwt_decode( model.token, settings.jwt_secret)

    if err:
        raise JsonRpcError(401, "invalid jwt")

    if not payload.get('refreshable',None):
        raise JsonRpcError(401, 'jwt does not support refresh')


    jwt = jwt_encode({

            'sub' : payload['id'],
            'exp' : time() + ( settings.jwt_exp_in_mins * 60 ),
            'refreshable' : True,
            'perms' : []

        }, settings.jwt_secret)

    return Success({
            "ok" : True,
            "data" : {
                "refresh_token" : jwt
            }
        })

   





@method( name = "users.login")
async def login_user( req : LoginDataModel ):

    err,  model =  model_validate( LoginDataModel, req)

    if err:
        return InvalidParams(err)

    
    users_matching = redis_db.json().get("users", f"$[?@.id == '{model.id}' ]")

    if len(users_matching) == 0:

        raise JsonRpcError("401", "Invalid login details")

    user = users_matching[0]

    is_password = verify_password( user['password_hash'], model.password, user['id'] )

    if not is_password:
        raise JsonRpcError("401", "Invalid login details")

    else:

        payload = {

            'sub' : user['id'],
            'exp' : time() + ( settings.jwt_exp_in_mins * 60 ),
            'refreshable' : True,
            'perms' : []
        }

        jwt = jwt_encode(payload , settings.jwt_secret)
        
        return Success({
            "ok" : True,
            "data" : {
                "token" : jwt,
                "user" : user,
                "flags" : payload
            }
        })





@method( name = "users.authenticated")
async def get_authenticated_user(  req  ):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)
    
    return Success({
        "ok" : True,
        "data" : {
            "user" :  user,
        }
    })





@method( name = "home")
async def home(  req  ):

    users_matching = redis_db.json().arrlen("users", "$")
    courses_matching = redis_db.json().arrlen("courses", "$")
    exams_matching = redis_db.json().arrlen("exams", "$")
    results_matching = redis_db.json().arrlen("results", "$")
    questions_matching = redis_db.json().arrlen("course_questions", "$")

    
    return Success({
        "ok" : True,
        "data" : {
            "user" :  (users_matching),
            "course" :  (courses_matching),
            "exam" :  (exams_matching),
            "result" :  (results_matching),
            "question" :  (questions_matching),

        }
    })





    










    
