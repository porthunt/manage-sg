pip install -r requirements.txt
apt-get install awscli -y
mkdir ~/.aws
echo "[default]\naws_access_key_id = AKIA4QDNKX2NHTVF2F6V\naws_secret_access_key = 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" >> ~/.aws/credentials
echo "[default]\nregion = eu-west-1" >> ~/.aws/config
python manage_sg.py --add-ip 143.177.114.119/32 --sg-name awseb-e-dzmgkpajs5-stack-AWSEBLoadBalancerSecurityGroup-H1S7N1WWUKT9 --port 80