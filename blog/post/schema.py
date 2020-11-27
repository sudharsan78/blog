import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import Post, PostComment


class PostType(DjangoObjectType):
    class Meta:
        model = Post


class PostCommentType(DjangoObjectType):
    class Meta:
        model = PostComment


class CreatePostMutation(graphene.Mutation):
    class Arguments:
        author = graphene.String()
        title = graphene.String()
        description = graphene.String()

    post = graphene.Field(PostType)

    @classmethod
    def mutate(cls, root, info, author, title, description):
        post = Post.objects.create(author=author, title=title, description=description)
        return CreatePostMutation(post=post)


class UpdatePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        author = graphene.String()
        title = graphene.String()
        description = graphene.String()

    post = graphene.Field(PostType)

    @classmethod
    def mutate(cls, root, info, id, author=None, title=None, description=None):
        try:
            post = Post.objects.get(pk=id)
            post.author = author if author is not None else post.author
            post.title = title if title is not None else post.title
            post.description = description if description is not None else post.description
            post.save()
        except Post.DoesNotExist:
            raise GraphQLError(f'Could not find the post with the given id: {id}')
        return UpdatePostMutation(post=post)


class DeletePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    is_deleted = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        try:
            Post.objects.get(pk=id).delete()
        except Post.DoesNotExist:
            raise GraphQLError(f'Could not find the post with the given id: {id}')
        return DeletePostMutation(is_deleted=True)


class CreateCommentMutation(graphene.Mutation):
    class Arguments:
        post = graphene.ID()
        comment = graphene.String()
        author = graphene.String()

    comment = graphene.Field(PostCommentType)

    @classmethod
    def mutate(cls, root, info, post, comment, author):
        try:
            post_obj = Post.objects.get(pk=post)
            comment_obj = PostComment.objects.create(author=author, comment=comment, post=post_obj)
        except Post.DoesNotExist:
            raise GraphQLError(f'Could not find the post with the given post_id: {post}')

        return CreateCommentMutation(comment=comment_obj)


class DeleteCommentMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    is_deleted = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        try:
            PostComment.objects.get(pk=id).delete()
        except PostComment.DoesNotExist:
            raise GraphQLError(f'Could not find the comment with the given id: {id}')
        return DeletePostMutation(is_deleted=True)


class Query(graphene.ObjectType):
    posts = graphene.List(PostType)
    post = graphene.Field(PostType, id=graphene.ID())

    def resolve_posts(self, info, **kwargs):
        return Post.objects.all()

    def resolve_post(self, info, id):
        return Post.objects.prefetch_related("postcomment_set").get(pk=id)


class Mutation(graphene.ObjectType):
    create_post = CreatePostMutation.Field()
    update_post = UpdatePostMutation.Field()
    delete_post = DeletePostMutation.Field()

    create_comment = CreateCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()

