FROM golang:1.17.1-alpine as builder

WORKDIR /go/src/app
COPY app.go ./
RUN apk add --update --no-cache gcc musl-dev git
RUN go mod init && \
	go mod tidy && \
	go build -o app .

FROM alpine:latest
WORKDIR /srv

COPY --from=builder /go/src/app/app app
COPY tmpl /app

RUN addgroup -g 1001 -S ci && \
    adduser -u 1001 -S -g ci ci && \
    chown -R ci:ci /app && chmod -R 555 /app

USER ci
EXPOSE 8000
CMD ["./app"]