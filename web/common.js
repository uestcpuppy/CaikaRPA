function Substr(str, start, n) { // eslint-disable-line
    if (str.replace(/[\u4e00-\u9fa5]/g, '**').length <= n) {
    return str;
    }
    let len = 0;
    let tmpStr = '';
    for (let i = start; i < str.length; i++) { // �����ַ���
    if (/[\u4e00-\u9fa5]/.test(str[i])) { // ���� ����Ϊ���ֽ�
      len += 2;
    } else {
      len += 1;
    }
    if (len > n) {
      break;
    } else {
      tmpStr += str[i];
    }
    }
    return tmpStr;
}
// nΪ��Ҫ��������ڲ�������ǰΪ0��ǰһ��Ϊ-1����һ��Ϊ1
function formatDate(n){
     var date = new Date() ;
     var year,month,day ;
     date.setDate(date.getDate()+n);
     year = date.getFullYear();
     month = date.getMonth()+1;
     day = date.getDate() ;
     s = year + '-' + ( month < 10 ? ( '0' + month ) : month ) + '-' + ( day < 10 ? ( '0' + day ) : day) ;
     return s ;
}
