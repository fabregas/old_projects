import sys,os

TAB_NUM = 4

def replace( tabbed_str ):
    lines = tabbed_str.split('\n')

    ret_lines = [line.replace('\t',' '*TAB_NUM) for line in lines]

    return '\n'.join(ret_lines)


if __name__ == '__main__':
    if len(sys.argv) < 2:
       print ("replace_tabs.py <file name>")
       sys.exit(-1)

    f_name = sys.argv[1]

    f = open(f_name)
    text = f.read()
    f.close()

    ret_text = replace(text)

    os.system("cp %s %s"%(f_name, os.path.join('/tmp',os.path.basename(f_name))))
    f = open(f_name,'w')
    f.write(ret_text)
    f.close()

    print("OK")
