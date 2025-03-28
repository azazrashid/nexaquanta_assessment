from app.models.blog import BlogPost
from app.repositories.base_repo import BaseRepo


class BlogRepository(BaseRepo[BlogPost]):
    """
    Blog repository provides all the database operations for the BlogPost model.
    """

    def __init__(self):
        super().__init__(BlogPost)
