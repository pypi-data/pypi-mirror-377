from pydantic import BaseModel, Field


class translateSQL(BaseModel):
    domain: str = Field(description="Is name of the process that the user wants to migrate or translate")
    filename: str = Field(description="Is the name of the file the user wants to translated, belongs to a domain")
    user_requirement: str = Field(description="Is the migration process that the user wants to do, example migrate from sql server to redshift")
    target_type: str = Field(description="Is the sql target type the user wants as output")


class debugSQl(BaseModel):
    pipeline_name: str = Field(description="Is name of the process or pipeline that the user wants to fix or debug")
    user_requirement: str = Field(description="Is the fix process that the user wants to do")
    test_case_name: str = Field(description="Is the test case that the user wants to check")
