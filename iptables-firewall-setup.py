import subprocess

def run_cmd(command):
    """Komutları çalıştırır ve hata mesajlarını yönetir."""
    try:
        # Komutun çıktısını al ve işle
        result = subprocess.run(f"sudo {command}", shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Başarılı: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Hata: {e.stderr}")
        print(f"Komut başarısız oldu: {command}")

def setup_firewall():
    """Güvenlik duvarı kurallarını uygular."""
    
    # Zincirin zaten var olup olmadığını kontrol et ve yalnızca yoksa oluştur
    run_cmd("sudo iptables -L myfirewall.rules -n > /dev/null 2>&1 || sudo iptables -t filter -N myfirewall.rules")
    
    # Yerel loopback arayüzüne izin ver
    run_cmd("sudo iptables -A myfirewall.rules -p all -i lo -j ACCEPT")

    # Tüm ICMP trafiğine izin ver
    run_cmd("sudo iptables -A myfirewall.rules -p icmp --icmp-type any -j ACCEPT")

    # VPN için gerekli protokoller ve portlar
    run_cmd("sudo iptables -A myfirewall.rules -p 50 -j ACCEPT")  # ESP
    run_cmd("sudo iptables -A myfirewall.rules -p 51 -j ACCEPT")  # AH
    run_cmd("sudo iptables -A myfirewall.rules -p udp --dport 500 -j ACCEPT")     # IKE
    run_cmd("sudo iptables -A myfirewall.rules -p udp --dport 10000 -j ACCEPT")   # IPSec UDP
    run_cmd("sudo iptables -A myfirewall.rules -p tcp --dport 443 -j ACCEPT")     # IPSec TCP + HTTPS

    # mDNS (multicast DNS)
    run_cmd("sudo iptables -A myfirewall.rules -p udp --dport 5353 -d 224.0.0.251 -j ACCEPT")

    # IPP (Internet Printing Protocol)
    run_cmd("sudo iptables -A myfirewall.rules -p udp --dport 631 -j ACCEPT")

    # Daha önce kurulmuş bağlantılara izin ver
    run_cmd("sudo iptables -A myfirewall.rules -p all -m state --state ESTABLISHED,RELATED -j ACCEPT")

    # SSH erişimine izin ver
    run_cmd("sudo iptables -A myfirewall.rules -p tcp --dport 22 -j ACCEPT")

    # HTTP sunucusuna izin ver
    run_cmd("sudo iptables -A myfirewall.rules -p tcp --dport 80 -j ACCEPT")

    # Diğer tüm paketleri reddet
    run_cmd("sudo iptables -A myfirewall.rules -p all -j REJECT --reject-with icmp-host-prohibited")

    # myfirewall.rules zincirini INPUT ve FORWARD zincirlerinin başına ekle
    run_cmd("sudo iptables -I INPUT -j myfirewall.rules")
    run_cmd("sudo iptables -I FORWARD -j myfirewall.rules")

if _name_ == "_main_":
    # Güvenlik duvarını yapılandır
    setup_firewall()
    print("Güvenlik duvarı kuralları başarıyla uygulandı.")