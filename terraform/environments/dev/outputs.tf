output "vpc_id" {
  value = module.vpc.vpc_id
}

output "subnet_id" {
  value = module.vpc.subnet_id
}

output "security_group_id" {
  value = module.vpc.security_group_id
}

output "instance_id" {
  value = module.ec2.instance_id
}

output "private_ip" {
  value = module.ec2.private_ip
}

output "public_ip" {
  value = module.ec2.public_ip
}

output "bucket_name" {
  value = module.s3.bucket_name
}

output "bucket_arn" {
  value = module.s3.bucket_arn
}

output "iam_role_arn" {
  value = module.iam.role_arn
}

output "instance_profile_name" {
  value = module.iam.instance_profile_name
}
