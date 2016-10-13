# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

def get_user_name_from_email(email):
    """Returns a string corresponding to the user first and last names,
    given the user email."""
    u = db(db.auth_user.email == email).select().first()
    if u is None:
        return 'None'
    else:
        return ' '.join([u.first_name, u.last_name])


def index():
    """
    This is your main controller.
    """
    # I am creating a bogus list here, just to have some divs appear in the
    # view.  You need to read at most 20 posts from the database, in order of
    # most recent first, and you need to return that list here.
    # Note that posts is NOT a list of strings in your actual code; it is
    # what you get from a db(...).select(...).
    #posts = ['banana', 'pear', 'eggplant']
    posts = db(db.post).select()
    posts = posts.sort(lambda posts: posts.created_on)
    names = list()
    for i in posts:
        names.append(get_user_name_from_email(i.user_email))
    #for i in posts:
    #    names = (i, get_user_name_from_email(i.user_email))
    return dict(posts=posts, names=names)
    #return dict(names=names)


@auth.requires_login()
def edit():
    """
    This is the page to create / edit / delete a post.
    if there are no arguments passsed to edit, user is provided with form
         to create a new post
    if there is an argument(args=[post_id]), then user can edit post with
         id post_id
         -check that the specified post exists
         - if the post exists check that the post was created by the logged in user
    """

    if request.args(0) is None:
        form = SQLFORM(db.post)

    else:
        #post_querry =db(db.post.id==request.args(0) and db.post.user_email==auth.user.email).select().first()
        post_querry = db(db.post.user_email==auth.user.email and db.post.id==request.args(0)).select().first()
        if post_querry is None or post_querry.user_email != auth.user.email:
            session.flash = T('Not authorized to edit this post')
            redirect(URL('default', 'index'))
        form = SQLFORM(db.post, record=post_querry, deletable=False, readonly=False)
        #post_querry.updated_on = datetime.datetime.utcnow()

    if form.process().accepted:
        redirect(URL('default', 'index'))

    return dict(form=form)



def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


