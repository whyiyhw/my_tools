package main

import (
	"github.com/gin-gonic/gin"
	"webhook/app"
	"webhook/config"
)

func main() {
	r := gin.Default()

	r.GET(config.BaseRoute, app.DealRequestToExecShell)

	err := r.Run()

	if err != nil {
		return
	}
}
