
* 프로토콜 URI 표기법

- push

gcm://[token]
apns://[token]

Example:
apns://473289475938267895402435478684573498547421

- sms

sms://[cell number]

Example:
sms://01020201234

- model 

model://[primary key]@[model name]

[model name]에 따라서 해당 파서가 호출됨. 없을 경우 message.parser.default_parser 호출

Example:
model://421412@mymodel


* 파서 형식

선언: 
def parser(obj, priority=('push','sms',)):

결과값: 
List of uri

* default_parser 동작 

1. URI에서 폴더 지정 시 최우선 순위
model://[pk]@[model]/[field]

Example
model://421412@mymodel/phone

2. Model 구조에 기본 필드  검색
token & cell



