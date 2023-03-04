<?php
# 读取指定文件的json
$configPath = "xxxxxxxxxxxx";
$url        = "xxxxxxxxxxxxxxxxxxxx";

$pingAddress = function () {
    $status = -1;
    if (strcasecmp(PHP_OS, 'WINNT') === 0) {
        // Windows 服务器下
        $pingResult = exec("curl -x socks5://127.0.0.1:1080 https://api.openai.com/v1/completions -v", $outcome, $status);
    } elseif (strcasecmp(PHP_OS, 'Linux') === 0) {
        // Linux 服务器下
        $pingResult = exec("curl -x socks5://127.0.0.1:1080 https://api.openai.com/v1/completions -v", $outcome, $status);
        echo $pingResult . PHP_EOL;
    }
    if (0 === $status) {
        $status = true;
    } else {
        $status = false;
    }
    return $status;
};


$configStr = file_get_contents($configPath);
try {
    $configArray = json_decode($configStr, true, 512, JSON_THROW_ON_ERROR);

    # 判断json 中的地址 是否能ping 通？
    if (isset($configArray['outbounds'][0]['settings']['vnext'][0]['address'])) {
        $address = $configArray['outbounds'][0]['settings']['vnext'][0]['address'];
        $pingAddress() && exit("ok");
        echo "current serve ping exception" . PHP_EOL;
    }
} catch (JsonException $e) {
    exit("error: 解析json 异常 ");
}


# 不能 ping 通进入更新流程

# 请求URL
$data = file_get_contents($url);

$arr = explode(PHP_EOL, base64_decode($data));

if (count($arr) === 0) {
    exit("没有获取到数据");
}

$list = [];

foreach ($arr as $value) {

    $value = trim($value);

    if (strpos($value, "ss://") === 0) {

        [$needDecodeData, $name] = explode("#", substr($value, 5));

        $tmp = explode(":", base64_decode($needDecodeData));

        $list["ss"][] = [
            "name"     => $name,
            "type"     => "ss",
            "server"   => explode("@", $tmp[1])[1],
            "port"     => (int)$tmp[2],
            "password" => explode("@", $tmp[1])[0],
            "cipher"   => $tmp[0],
        ];
        continue;
    }

    if (strpos($value, "vmess://") === 0) {

        $tmp = json_decode(base64_decode(substr($value, 8)), true);

        $list["vmess"][] = [
            "name"             => $tmp["ps"],
            "type"             => "vmess",
            "server"           => $tmp["add"],
            "port"             => (int)$tmp["port"],
            "cipher"           => "auto",
            "uuid"             => (string)$tmp["id"],
            "alterId"          => (int)$tmp["aid"],
            "tls"              => ($tmp["tls"] !== "none"),
            "skip-cert-verify" => true,
            "servername"       => "",
            "network"          => $tmp["net"],
        ];
    }
}

if (count($list) === 0 || empty($list["vmess"])) {
    exit("没有获取到 vmess 数据");
}

foreach ($list["vmess"] as $vmess) {
    $configArray['outbounds'][0]['settings']['vnext'][0]['address']             = $vmess["server"];
    $configArray['outbounds'][0]['settings']['vnext'][0]['port']                = $vmess["port"];
    $configArray['outbounds'][0]['settings']['vnext'][0]['users'][0]['id']      = $vmess["uuid"];
    $configArray['outbounds'][0]['settings']['vnext'][0]['users'][0]['alterId'] = $vmess["alterId"];
    $configArray['outbounds'][1]['settings']                                    = (object)$configArray['outbounds'][1]['settings'];
    $last                                                                       = json_encode($configArray, JSON_THROW_ON_ERROR);
    file_put_contents($configPath, $last);
    exec("docker restart v2ray");
    sleep(2);
    $pingAddress() && exit("change successful");
}
