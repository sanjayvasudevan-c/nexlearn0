from pydantic import BaseModel

class NotesResponse(BaseModel):

    id : str 
    title : str
    subject : str
    file_type : str
    file_size : int

    class Config:
        from_attributes = True


