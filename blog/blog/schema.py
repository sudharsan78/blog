import graphene

from post.schema import Query as PostSchema, Mutation as PostMutation


class Query(PostSchema, graphene.ObjectType):
    pass


class Mutation(PostMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
