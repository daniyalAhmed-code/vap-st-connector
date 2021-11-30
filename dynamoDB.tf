module "categories_table" {
  source = "./vendor/dynamodb"

  name      = "${var.name}-categories"
  hash_key  = "Category"
  range_key = "SubCategory"

  attributes = [
    {
      name = "Category"
      type = "S"
    },
    {
      name = "SubCategory"
      type = "S"
    }
  ]
}

module "activities_table" {
  source = "./vendor/dynamodb"

  name      = "${var.name}-activities"
  hash_key  = "PK"
  range_key = "SK"

  local_secondary_indexes = [{
    name            = "TIMS"
    range_key       = "Result"
    projection_type = "ALL"
  }]

  attributes = [
    {
      name = "PK"
      type = "S"
    },
    {
      name = "SK"
      type = "S"
    },
    {
      name = "Result"
      type = "S"
    }
  ]
}