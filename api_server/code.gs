/**
 * =========================
 * C_Assistant_Protocol v2.2
 * (UI + Dynamic JSON API)
 * =========================
 * - C님의 'doPost'/'appendHandoff' 로직 (UI, 쓰기) 채택
 * - v2.0의 '보안 (PropertiesService)' 및 '동적 JSON (읽기)' 로직 결합
 */

// [사용자 설정] 이 GDoc ID는 본인의 GDoc ID로 수정하세요.
var DOC_ID = '13hkVp2_6s2AcVgtcRUtMyqXCGGCJfjOkJWvq-XCgyu4';

/**
 * [보안] 스크립트 속성에서 API 토큰(비밀번호)을 안전하게 가져옵니다.
 */
function getSecret() {
  return PropertiesService.getScriptProperties().getProperty('API_TOKEN');
}

/**
 * [READ] GET 요청 처리 (UI 또는 JSON 데이터)
 * mode=ui    : (기본값) HTML 웹페이지 UI를 로드합니다.
 * mode=json  : (보안) 최신 핸드S오프 블록을 '동적 JSON'으로 반환합니다.
 */
function doGet(e) {
  var m = (e && e.parameter && e.parameter.mode) || 'ui';

  // 1. JSON API 모드 (Python/Tasker용)
  if (m === 'json') {
    var key = (e && e.parameter && e.parameter.key) || '';
    // v2.2 보안: API 토큰 검사
    if (key !== getSecret()) {
      return createJSON({ error: 'UNAUTHORIZED' });
    }
    // v2.2 기능: 텍스트가 아닌 'JSON' 반환
    return createJSON(getLatestAsJSON());
  }
  
  // 2. UI 모드 (웹 브라우저용)
  // (보안 토큰 없이도 UI 페이지 자체는 로드할 수 있도록 허용)
  return HtmlService.createHtmlOutputFromFile('ui')
    .setTitle('Memory Handoff Hub')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * [WRITE] POST 요청 처리 (외부 자동화 도구용)
 * Tasker, Python 등에서 GDoc에 [HANDOFF] 블록을 '쓰기' 위해 사용합니다.
 */
function doPost(e) {
  var key = (e && e.parameter && e.parameter.key) || '';

  // v2.2 보안: API 토큰 검사
  if (key !== getSecret()) {
    return createJSON({ error: 'UNAUTHORIZED' });
  }

  // C님의 'text/plain' 및 'form-data' 동시 지원 로직 (우수함)
  var text = '';
  if (e && e.postData && e.postData.contents) text = String(e.postData.contents);
  if (!text && e && e.parameter && e.parameter.text) text = String(e.parameter.text);

  var res = appendHandoff(text); // C님의 뛰어난 '쓰기' 함수 호출
  return createJSON(res); // 결과를 JSON으로 반환
}

// ==========================================================
//  v2.2 Helper Functions (C님 로직 + v2.0 로직)
// ==========================================================

/**
 * [CORE UPGRADE] 최신 핸드오프를 '동적 JSON'으로 파싱합니다.
 * v2.0의 핵심 로직을 여기에 통합합니다.
 */
function getLatestAsJSON() {
  const latestHandoffText = getLatestAsText(); // 1. 최신 텍스트 가져오기
  
  // 2. v2.0 동적 파싱 로직
  const regex = /\[([a-zA-Z0-9_ ]+)\]([\s\S]*?)(?=\n\[[a-zA-Z0-9_ ]+\]|$)/g;
  let sectionMatch;
  const result = {
    parsed_at: new Date().toISOString()
  };

  // [HANDOFF] 블록인지 확인
  if (!/^\s*\[HANDOFF\]/.test(latestHandoffText)) {
     // 핸드오프 블록이 아니면, 전체를 'content'로 반환
     result["content"] = latestHandoffText;
     return result;
  }

  // 3. 동적으로 JSON 객체 생성
  while ((sectionMatch = regex.exec(latestHandoffText)) !== null) {
    const key = sectionMatch[1].trim();
    const value = sectionMatch[2].trim();
    if (key !== "HANDOFF") { // [HANDOFF] 태그 자체는 제외
        result[key] = value;
    }
  }
  return result;
}

/**
 * (C님 로직) GDoc에 텍스트를 '쓰는' 핵심 함수.
 * (수정 없음, 매우 훌륭한 로직)
 */
function appendHandoff(text) {
  text = (text || '').trim();
  if (!text) return {status:'NO_TEXT'};

  var now = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm');
  var doc = DocumentApp.openById(DOC_ID);
  var body = doc.getBody();

  body.appendParagraph('---'); // 블록 위쪽에 구분선

  if (!/^\s*\[HANDOFF\]/.test(text)) {
    body.appendParagraph('[HANDOFF] ' + now + ' KST');
  }

  text.split(/\r?\n/).forEach(function(line){
    body.appendParagraph(line);
  });

  doc.saveAndClose();
  return {
    status: 'OK',
    url: 'https://docs.google.com/document/d/' + DOC_ID + '/edit',
    name: DocumentApp.openById(DOC_ID).getName()
  };
}

/**
 * (C님 로직) 최신 블록을 '순수 텍스트'로 가져옵니다. (JSON 파서의 재료)
 */
function getLatestAsText() {
  var doc = DocumentApp.openById(DOC_ID);
  var t = doc.getBody().getText();
  var parts = t.split(/\n---\n/g); // C님의 '---' 구분선 로직
  return (parts[parts.length - 1] || t).trim();
}

/**
 * (C님 로직) UI에서 '문서 열기'용 정보를 가져옵니다.
 */
function getDocInfo() {
  var doc = DocumentApp.openById(DOC_ID);
  return {
    id: DOC_ID,
    url: 'https://docs.google.com/document/d/' + DOC_ID + '/edit',
    name: doc.getName()
  };
}

/**
 * (v2.0 로직) JSON 응답을 생성합니다.
 */
function createJSON(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}