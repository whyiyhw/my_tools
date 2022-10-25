package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
	"time"
)

func main() {
	fmt.Println("svn auto commit start")

	// 基础配置
	currTime := time.Now().Local()
	basePath := "C:\\workFile\\SVN16\\语雀文档\\技术分享\\技术类\\redis\\svn\\"

	// 改变当前工作目录
	_ = os.Chdir(basePath)
	fmt.Println(os.Getwd())

	// 覆盖写内容
	fileName := currTime.Format("2006-01-02") + ".txt"
	err := runInWindowsWithErr(
		"echo " + currTime.Format("2006-01-02 15:04:05") + " svn auto commit by golang > " + fileName,
	)
	if err != nil {
		return
	}
	//svn add
	err = runInWindowsWithErr("svn add " + fileName + " --force")
	if err != nil {
		return
	}
	// svn commit
	err = runInWindowsWithErr("svn commit " + fileName + " -m \"\" ")
	if err != nil {
		return
	}
	fmt.Println("svn auto commit end ✨")
}

func runInWindowsWithErr(cmd string) error {
	fmt.Println("Running Windows cmd:" + cmd)
	result, err := exec.Command("cmd", "/c", cmd).Output()
	if err != nil {
		fmt.Println(err.Error())
		return err
	}
	fmt.Println(strings.TrimSpace(string(result)))
	return nil
}
