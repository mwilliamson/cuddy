from datetime import datetime

import collections

import cuddy


Author = collections.namedtuple(
    "Author",
    ["name"]
)

BlogPost = collections.namedtuple(
    "BlogPost",
    ["title", "author", "created_date"]
)

bob = Author("Bob")

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


class BlogPostAdmin(object):
    name = "Blog post"
    slug = "blog-post"
    
    fields = [
        cuddy.field("Title", "title", type=cuddy.string),
        cuddy.field("Author", "author", type=AuthorAdmin),
        cuddy.field("Date", "created_date", type=cuddy.datetime),
    ]
    
    def fetch_all(self):
        return [
            BlogPost("Apples", created_date=datetime(2013, 9, 5), author=bob),
            BlogPost("Bananas", created_date=datetime(2013, 9, 6), author=bob),
        ]
        

admin = cuddy.create()
admin.add(AuthorAdmin)
admin.add(BlogPostAdmin)

app = admin.wsgi_app()
