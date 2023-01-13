﻿from jsonrpcserver import method, JsonRpcError, InvalidParams, Success
from lib.db import redis_db
from lib.utils import model_validate, authenticate_user, validate_req
from models.exams import CreateExamInputModel, CreateExamSessionInput, ResumeExamSessionInput, ExamSession
from models.settings import Settings
from time import time
import rsa
import random

settings = Settings()


@method(name="exams.create")
async def add_new_exam(req):
    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    err, model = model_validate(CreateExamInputModel, req.body)

    if err:
        return InvalidParams(err)

    data = model.dict()

    matching_courses = redis_db.json().get(
        "courses", f"$[?@.id == '{model.course_id}' ]")

    if len(matching_courses) == 0:
        raise JsonRpcError(403, "Course specified does not exist")

    matching = redis_db.json().get(
        "exams", f"$[?@.exam_title == '{model.exam_title}' ]")

    if len(matching) > 0:
        raise JsonRpcError(403, "exam with title exists already")

    data.update({
        "course": matching_courses[0]
    })

    redis_db.json().arrappend("exams", "$", data)

    return Success({
        "ok": True,
        "data": model.dict(by_alias=True)
    })


@method(name="exams.list")
async def list_all_exam(req):
    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    matching = redis_db.json().get("exams", f"$")

    return Success({
        "ok": True,
        "data": matching[0]
    })


@method(name="exams.get_one")
async def get_one_exam(req):
    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    id = req.body['id']

    matching = redis_db.json().get("exams", f"$[?@.id == '{id}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "exam with id does not exists")

    return Success({
        "ok": True,
        "data": matching[0]
    })


@method(name = "exams.session.heartbeat")
async def session_heartbeat(req):
    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    session = redis_db.json().set(f"examsession:{user['id']}", "$.last_ping", time() )

    session_model = ExamSession(**session)

    return Success({
        "ok": True,
        "data": session_model.dict(exclude={'private_key', 'public_key'})
    })



@method(name="exams.create_session")
async def create_exam_session(req):
    
    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    err, model = model_validate(CreateExamSessionInput, req.body)
    
    if err:
        return InvalidParams(err)
        
    matching = redis_db.json().get("exams", f"$[?@.id == '{model.exam}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "exam with id does not exist")

    exam = matching[0]
        
    public_key = rsa.PublicKey.load_pkcs1(model.key)

    pub_key, priv_key = rsa.newkeys(512)

    peer_key  = pub_key.save_pkcs1()


  
    all_qids = redis_db.json().get("course_questions",f"$[?@.course == '{exam['course']['id']}'].id" )

    number_of_questions_in_course = len(all_qids)

    if number_of_questions_in_course == 0:
        raise JsonRpcError(403, "No questions for seleceted course")


    qids = []


    start = 0
    while start < exam['number_of_questions']:
        start += 1
        x = random.randint(0, number_of_questions_in_course -1)
        qids.append(all_qids[x])


    session = ExamSession(
        peer_public_key = public_key.save_pkcs1(),
        private_key = priv_key.save_pkcs1(),
        public_key = peer_key,
        exam = model.exam,
        user = user['id'],
        ping_interval = settings.ping_interval,
        question_ids = qids
    )

    session_dict = session.dict()

    redis_db.json().set(f"examsession:{user['id']}", "$", session_dict )


    return Success({
        "ok": True,
        "data": session.dict(exclude={'private_key', 'public_key'})
    })



    