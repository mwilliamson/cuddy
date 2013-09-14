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
    
    fields = [
        cuddy.field("name", type=cuddy.string)
    ]

class BlogPostAdmin(object):
    name = "Blog post"
    fields = [
        cuddy.field("title", type=cuddy.string),
        cuddy.field("author", type=AuthorAdmin),
        cuddy.field("created_date", type=cuddy.datetime),
    ]
    
    def fetch_all(self):
        return [
            BlogPost("Apples", datetime(2013, 9, 5), author=bob),
            BlogPost("Bananas", datetime(2013, 9, 6), author=bob),
        ]
        

admin = cuddy.create()
admin.add(AuthorAdmin)
admin.add(BlogPostAdmin)

app = admin.wsgi_app()
