from datetime import datetime
import collections

import zuice

import cuddy


Author = collections.namedtuple(
    "Author",
    ["name"]
)

BlogPost = collections.namedtuple(
    "BlogPost",
    ["id", "title", "author", "created_date"]
)

bob = Author("Bob")


class PostsRepository(object):
    def __init__(self):
        self._posts = [
            BlogPost(1, "Apples", created_date=datetime(2013, 9, 5), author=bob),
            BlogPost(4, "Bananas", created_date=datetime(2013, 9, 6), author=bob),
        ]
        
    def fetch_all(self):
        return self._posts
        
    def fetch_by_id(self, id):
        for post in self._posts:
            if post.id == id:
                return post


class AuthorAdmin(object):
    name = "Author"
    slug = "author"
    
    fields = [
        cuddy.field("Name", "name", type=cuddy.string)
    ]
    
    def short_describe(self, author):
        return author.name
    
    def fetch_all(self):
        return [bob]


class BlogPostAdmin(zuice.Base):
    _repository = zuice.dependency(PostsRepository)
    
    name = "Blog post"
    slug = "blog-post"
    
    fields = [
        cuddy.field("Title", "title", type=cuddy.string),
        cuddy.field("Author", "author", type=AuthorAdmin),
        cuddy.field("Date", "created_date", type=cuddy.datetime),
    ]
    
    edit_link_field = "Title"
    
    def short_describe(self, post):
        return post.title
    
    def fetch_all(self):
        return self._repository.fetch_all()
        
    def identify(self, post):
        return post.id
        
    def fetch_by_id(self, id):
        try:
            id = int(id)
        except ValueError:
            return None
        else:
            return self._repository.fetch_by_id(id)


admin = cuddy.create()
admin.add(AuthorAdmin)
admin.add(BlogPostAdmin)

app = admin.wsgi_app()
