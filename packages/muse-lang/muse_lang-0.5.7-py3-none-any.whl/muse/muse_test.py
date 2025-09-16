import muse.muse_lang as ml
import muse.sample as sample

def test_code(code):
    print(ml.ast_check(code))
    result = ml.trial(code)
    if result['code'] == 'SUCCESS':
        print(result['data'])
        if 'error_msg' in result and result['error_msg'] != '':
            print(result['error_msgs'])
    else:
        print(result['error_msgs'])


def test_all():
    i = 1
    for s in sample.demos:
        print(f'-------demo{i}--------')
        test_code(s)
        i += 1

if __name__ == '__main__':
    test_all()
    # test_code(sample.demo10)