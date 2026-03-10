import csv
import os

def generate_vless_links():
    print("="*40)
    print("      VLESS 批量链接生成器 (交互版)")
    print("="*40)
    
    # 1. 获取 CSV 文件路径
    default_csv = "result.csv"
    csv_file_path = input(f"\n[1] 请输入 result.csv 的路径 (直接回车默认使用当前目录下的 {default_csv}): ").strip()
    if not csv_file_path:
        csv_file_path = default_csv
        
    if not os.path.exists(csv_file_path):
        print(f"\n❌ 错误: 找不到文件 {csv_file_path}")
        return

    # 2. 获取输出文件路径
    default_output = "vless_links_output.txt"
    output_file_path = input(f"\n[2] 请输入输出文件的路径 (直接回车默认使用当前目录下的 {default_output}): ").strip()
    if not output_file_path:
        output_file_path = default_output

    # 3. 获取链接模板
    print("\n[3] 请输入 VLESS 链接模板。")
    print("    👉 请在模板中使用 {ip} 代表优选IP，使用 {index} 代表序号。")
    print("    👉 示例: vless://0b04dd5a-c696-4bb2-b781-5babcef450be@{ip}:8443?encryption=none&security=tls&sni=es.000486000.xyz&fp=chrome&alpn=h2%2Chttp%2F1.1&insecure=0&allowInsecure=0&type=xhttp&host=es.000486000.xyz&path=%2Fapi%2Fv3%2Fsync%2Fdata&mode=auto#IP{index}")
    
    template = input("\n请输入链接模板: ").strip()
    
    if not template:
        print("\n❌ 错误: 链接模板不能为空！")
        return
        
    if "{ip}" not in template:
        print("\n⚠️ 警告: 您的模板中没有包含 {ip} 占位符，生成的链接将不会包含 IP 地址！")

    links = []
    
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            # 跳过表头
            next(reader, None)
            
            # 遍历每一行，提取 IP 并生成链接
            for index, row in enumerate(reader, start=1):
                if not row:
                    continue
                ip = row[0].strip()
                if ip:
                    try:
                        # 替换模板中的 {ip} 和 {index}
                        link = template.format(ip=ip, index=index)
                        links.append(link)
                    except KeyError as e:
                        print(f"\n❌ 模板格式错误，未知的占位符: {e}")
                        print("请确保模板中只使用了 {ip} 和 {index} 作为占位符。")
                        return
                    except ValueError as e:
                        print(f"\n❌ 模板格式错误: {e}")
                        print("如果您的链接中包含大括号 {}，请将它们写成双大括号 {{}} 以避免冲突。")
                        return
                    
        # 将生成的链接写入输出文件
        with open(output_file_path, mode='w', encoding='utf-8') as out_file:
            for link in links:
                out_file.write(link + '\n')
                
        print("\n" + "="*40)
        print(f"✅ 成功生成了 {len(links)} 个 VLESS 分享链接！")
        print(f"📁 链接已保存至: {os.path.abspath(output_file_path)}")
        print("="*40)
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    generate_vless_links()
    input("\n按回车键退出...")
