import requests
import json

def test_system_status_api():
    try:
        # เปลี่ยน URL ให้ตรงกับเซิร์ฟเวอร์ของคุณ
        response = requests.get('http://localhost:5000/api/system-status')
        
        # ตรวจสอบว่าได้รับการตอบกลับ 200 OK
        if response.status_code == 200:
            print("✅ API ทำงานปกติ!")
            
            # แปลงข้อมูล JSON เป็นรูปแบบที่อ่านง่าย
            data = response.json()
            formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
            
            # บันทึกผลลัพธ์ลงไฟล์
            with open('api_test_result.json', 'w', encoding='utf-8') as f:
                f.write(formatted_json)
            
            print(f"💾 บันทึกผลลัพธ์ลงไฟล์ api_test_result.json แล้ว")
            
            # แสดงข้อมูลสำคัญ
            print("\n📊 ข้อมูลสำคัญ:")
            print(f"🖥️  CPU: {data['cpu']['percent']}%")
            print(f"🧠 RAM: {data['memory']['percent']}%")
            print(f"💿 Disk: {data['disk']['percent']}%")
            print(f"⏱️  Uptime: {data['uptime']['days']} วัน {data['uptime']['hours']} ชั่วโมง")
            
        else:
            print(f"❌ เกิดข้อผิดพลาด: ได้รับรหัส HTTP {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")

if __name__ == "__main__":
    test_system_status_api()
