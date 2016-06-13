import pika
import subprocess
import sys

def get_path():
    try:
        path = sys.argv[1]
    except:
        print "no path provided, quitting."
        sys.exit()
    return path

def connections():
    channel = None
    connection = None
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='rabbitmq'))
        channel = connection.channel()

        channel.exchange_declare(exchange='topic_recs',
                                 type='topic')
    except:
        print "unable to connect to rabbitmq, quitting."
    return channel, connection

def parse_header(line):
    ret_dict = {}
    h = line.split()
    date = h[0]
    time = h[1]
    ret_dict['raw_header'] = line
    ret_dict['date'] = date
    ret_dict['time'] = time
    if h[2] == 'IP':
        #do something meaningful
        pass
    else:
        pass
        #do something else
    return ret_dict

def parse_data(line):
    ret_str = ''
    h,d = line.split(':', 1)
    ret_str = d.strip().replace(' ','')
    return ret_str

def return_packet(line_source):
    ret_data = ''
    expecting_header = True
    ret_header = {}
    ret_dict = {}
    for line in line_source:
        line_strip = line.strip()
        is_header = not line_strip.startswith('0x')
        if is_header:
            #parse header
            ret_header = parse_header(line)
            if not ret_data:
                #no data read, just update the header
                ret_dict.update(ret_header)
            else:
                #put the data into the structure and yeild
                ret_dict['data'] = ret_data
                ret_data=''
                yield ret_dict
        else:
            #concatenate the data
            data = parse_data(line_strip)
            ret_data = ret_data + data

def run_tool(path):
    routing_key = "tcpdump_hex_parser"+path.replace("/", ".")
    print "processing pcap results..."
    channel, connection = connections()
    proc = subprocess.Popen('tcpdump -nn -tttt -xx -r '+path, shell=True, stdout=subprocess.PIPE)
    for packet in return_packet(proc.stdout):
        message = str(packet)
        if channel != None:
            channel.basic_publish(exchange='topic_recs',
                                  routing_key=routing_key,
                                  body=message)
        print " [x] Sent %r:%r" % (routing_key, message)
    try:
        connection.close()
    except:
        pass

if __name__ == '__main__':
    path = get_path()
    run_tool(path)
