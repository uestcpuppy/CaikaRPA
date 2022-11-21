function Substr(str, start, n) { // eslint-disable-line
    if (str.replace(/[\u4e00-\u9fa5]/g, '**').length <= n) {
    return str;
    }
    let len = 0;
    let tmpStr = '';
    for (let i = start; i < str.length; i++) { // 遍历字符串
    if (/[\u4e00-\u9fa5]/.test(str[i])) { // 中文 长度为两字节
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
// n为你要传入的日期参数，当前为0，前一天为-1，后一天为1
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
