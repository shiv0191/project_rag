resource "aws_s3_bucket" "documents" {
  bucket = "${var.project_name}-documents"
}
