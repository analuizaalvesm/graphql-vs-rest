# REST and GraphQL equivalent queries for the experiment

rest_queries = {
    "simple": {
        "url": "/repos/facebook/react",
        "method": "GET",
    },
    "nested": {
        "url": "/repos/facebook/react/issues?state=open&per_page=10",
        "method": "GET",
    },
    "aggregated": {
        "urls": [
            "/repos/facebook/react",
            "/repos/facebook/react/contributors?per_page=5",
            "/repos/facebook/react/languages",
        ],
        "method": "GET",
    },
}

graphql_queries = {
    "simple":
    """
    query SimpleQuery {
      repository(owner: "facebook", name: "react") {
        id
        name
        description
        stargazerCount
        forkCount
        createdAt
        updatedAt
      }
    }
    """,
    "nested":
    """
    query NestedQuery {
      repository(owner: "facebook", name: "react") {
        id
        name
        description
        stargazerCount
        forkCount
        issues(first: 10, states: OPEN) {
          nodes {
            id
            title
            createdAt
            author { login }
            comments(first: 3) {
              nodes { id body createdAt author { login } }
            }
          }
        }
      }
    }
    """,
    "aggregated":
    """
    query AggregatedQuery {
      repository(owner: "facebook", name: "react") {
        id
        name
        description
        stargazerCount
        forkCount
        languages(first: 10) { nodes { name color } }
        collaborators(first: 5) { nodes { login name avatarUrl } }
        releases(first: 5) { nodes { id name tagName createdAt } }
      }
    }
    """,
}
