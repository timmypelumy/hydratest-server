﻿from pydantic import BaseModel, Field, HttpUrl, validator
from lib.utils import gen_uid
from typing import Union
from time import time
from enum import Enum

class CreateExamInputModel(BaseModel):
    id : str = Field( default_factory= gen_uid)
    exam_title : str = Field(min_length = 8, alias = "examTitle", )
    instant_result : bool = Field(alias = "instantResult")
    course_id : str  = Field(alias = "courseId", default= None)
    time_allowed : int = Field(alias = "timeAllowed")
    number_of_questions : int = Field( alias = "numberOfQuestions")

    @validator("exam_title")
    def to_lowercase(cls, v):
        return v.lower().strip()

    class Config:
        allow_population_by_field_name = True


# Initialize Exam Session Model
class CreateExamSessionInput( BaseModel ):
	key : str =Field( alias= "key")
	exam : str = Field( min_length = 8 )
	
	class Config:
		allow_population_by_field_name = True
		
		
		
# Resume a  Exam Session Model
class ResumeExamSessionInput( BaseModel ):
	public_key : str =Field( alias= "publicKey")
	
	
	class Config:
		allow_population_by_field_name = True



# Exam Session Response 
class ExamSessionResponse(BaseModel):
	id : str = Field( default_factory= gen_uid)
	session : str = Field( min_length = 8)
	question : str = Field( min_length = 8 )
	created : float = Field( min =0, default_factory = time )
	response : str = Field( min_length = 1)
	response_content : str = Field( min_length = 1 , alias = "responseContent")
	is_correct : bool = Field( default = False , alias = "isCorrect" )
	edits : int = Field( default  = 0 )
	integrity_hash : Union[None,str]= Field( default = None , min_length = 32 , alias = "integrityHash" )
	
	class Config:
		allow_population_by_field_name = True
	


# Exam Session Model 
class ExamSession(BaseModel):
	name : Union[None,str] = Field( default=None)
	peer_public_key : str =Field( alias= "peerPublicKey")
	public_key : str =Field( alias= "publicKey")
	private_key : str = Field( alias= "privateKey")
	id : str = Field( default_factory= gen_uid)
	exam : str = Field( min_length = 8 )
	user : str = Field(min_length = 6 )
	created : float = Field( min =0, default_factory = time )
	question_ids : list[str] = Field( min_items = 5, alias = "questionIds", default = [] )
	attempted_question_ids : list[str] =  Field( default = [], alias = "attemptedQuestionIds")
	ping_interval : int = Field( default = 5 , alias = "pingInterval" )
	last_ping : Union[None,float] = Field( default  = None, min = 0, alias = "lastPing" )
	elapsed_time : float = Field( default  = 0, min = 0, alias = "elapsedTime" )
	is_active : bool = Field( default = True, alias = "isActive" )
	submitted : bool = Field( default = False )
	result_generated : bool = Field(default= False, alias= "resultGenerated")
	
	
	class Config:
		allow_population_by_field_name = True


class GenerateResultInput(BaseModel):
	session_key : str = Field( alias='sessionKey', min_length= 8,  )
	is_regenerated : bool = Field(default= False, alias="isRegenerated")
	generate_pdf : bool = Field(default= False, alias="generatePdf")

	class Config:
		allow_population_by_field_name = True


class Remark(  str, Enum):
	_failed = "failed"
	_pass = "pass"
	_credit = "pass"
	_dinstinction = "distinction"
	_unknown = "unknown"

class Result(BaseModel):
	id : str = Field( default_factory= gen_uid)
	user : str = Field( min_length = 6 )
	exam : str = Field( min_length = 8 )
	course : str = Field( min_length = 8 )
	course_name : str = Field( min_length = 4 )
	exam_name : str = Field( min_length = 4 )
	correct_attempts   : int = Field( default= 0, alias="correctAttempts")
	incorrect_attempts : int = Field( default=0 ,alias= "incorrectAttempts")
	total_attempts : int = Field(default=0, alias="totalAttempts")
	attempts : int = Field(default=0, alias= "attempts")	
	score : float = Field(default= 0)
	remark : Remark
	session_key : str = Field( alias= "sessionKey" )
	created : float = Field( min =0, default_factory = time )
	allow_pdf : bool = Field(default = False, alias = "allowPdf")
	map_info : list[str] = Field(default= [],alias= "mapInfo" )



	class Config:
		allow_population_by_field_name = True
	









		




	
	