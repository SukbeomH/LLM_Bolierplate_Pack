# Frontend Dockerfile
# Next.js 프론트엔드 서버

FROM node:22-alpine

WORKDIR /app

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치
RUN npm install

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 3000

# 개발 서버 실행
CMD ["npm", "run", "dev"]
