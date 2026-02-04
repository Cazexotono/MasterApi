### Secret Storage Space
This is a storage of secret files that will be uploaded to the API.
#### Uploadable files
The following files are currently supported:
- rsa_private - Private key for working with JWT;
- rsa_public - Public key for working with JWT;

 **Files are added without extension**
#### Generating RSA keys
Make sure openssl is present on your system: 
```
openssl version
```
Command to generate a private key:
```
openssl genrsa -out rsa_private 4096
```
Command to generate a public key based on a private key:
```
openssl rsa -in rsa_private -pubout -out rsa_public
```