const XLSX = require('xlsx');
const workbook = XLSX.readFile('C:/Users/Administrator/.openclaw/media/inbound/file_3---0b15a695-4cd5-49a3-8b95-1fd05f7a6fe0.xlsx');
const sheetName = workbook.SheetNames[0];
const worksheet = workbook.Sheets[sheetName];
const data = XLSX.utils.sheet_to_json(worksheet);
console.log(JSON.stringify(data.slice(0, 10)));
