#!/bin/bash

pull_dir=$1
is_restart_fpm=$2

origin_host="github.com"
deploy_user="github"
deploy_password="github"


if [ $pull_dir ]; then
  # 去指定目录 自动 拉取 代码
  cd $pull_dir && echo "cd ${pull_dir}"
  # 获取原始地址
  originUrl=$(git config remote.origin.url)
  # 将 原始 originHost 替换为 user:password@originHost
  newUrl=${originUrl/$origin_host/$deploy_user:$deploy_password@$origin_host}
  # 设置
  git config remote.origin.url $newUrl
  # 拉取代码
  git pull 2>&1 && echo " git 拉取完成 "
  # 重新恢复环境变量
  git config remote.origin.url $originUrl
  # 查看目前的情况
  git config --list
  # 是否需要重载 fpm
  if [ $is_restart_fpm ]; then
    service php-fpm reload && echo "fpm 重载完成"
  else
    echo "不需要 重载 fpm"
  fi
else
  echo "git 项目目录不存在"
fi
