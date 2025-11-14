/*
 * [C_Assistant_Protocol v2.0 - Flexible API]
 * 이 스크립트는 *모든* GDoc의 최신 [HANDOFF] 블록을 동적으로 파싱합니다.
 * 템플릿의 섹션 이름이 변경되어도 코드를 수정할 필요가 없습니다.
 */
function doGet(e) {
  // 1. URL 파라미터에서 정보 추출
  const docId = e.parameter.docId;
  const token = e.parameter.token;
  
  // 2. (필수) 보안 토큰 검사
  // 이 토큰은 사용자가 직접 정하는 비밀번호입니다. (예: "C_SECRET_1234")
  // .env 파일의 API_TOKEN과 일치해야 합니다.
  const myToken = PropertiesService.getScriptProperties().getProperty('API_TOKEN');
  
  if (token !== myToken) {
    return createJSON({ error: "Access Denied. Invalid or missing token." });
  }
  if (!docId) {
    return createJSON({ error: "docId parameter missing." });
  }

  // 3. 문서 열기 및 최신 [HANDOFF] 블록 추출
  try {
    const body = DocumentApp.openById(docId).getBody().getText();
    const matches = body.match(/\[HANDOFF\][\s\S]*?(?=\n\[HANDOFF\]|$)/g);
    if (!matches || matches.length === 0) {
      return createJSON({ error: "No [HANDOFF] block found" });
    }
    const latestHandoff = matches[matches.length - 1];

    // 4. [핵심] 모든 [섹션]을 동적으로 파싱
    const regex = /\[([a-zA-Z0-9_ ]+)\]([\s\S]*?)(?=\n\[[a-zA-Z0-9_ ]+\]|$)/g;
    let sectionMatch;
    const result = {
      parsed_at: new Date().toISOString()
    };
    
    while ((sectionMatch = regex.exec(latestHandoff)) !== null) {
      const key = sectionMatch[1].trim();
      const value = sectionMatch[2].trim();
      if (key !== "HANDOFF") { // [HANDOFF] 태그 자체는 제외
          result[key] = value;
      }
    }

    // 5. JSON 결과 반환
    return createJSON(result);

  } catch (error) {
    return createJSON({ error: "Failed to open document or parse.", details: error.message });
  }
}

// JSON 반환 헬퍼 함수
function createJSON(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}