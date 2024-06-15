import graphene

import users.graphql.schema as user_schema

class Query(
    user_schema.Query,
):
    pass

class Mutation(
    user_schema.Mutation,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)