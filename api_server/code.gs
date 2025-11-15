/**
 * =========================
 * C_Assistant_Protocol v2.2+
 * (멀티 문서 + 카테고리 동기화)
 * =========================
 */

var DOC_ID = '13hkVp2_6s2AcVgtcRUtMyqXCGGCJfjOkJWvq-XCgyu4'; // 기본 개인 문서
var TEAM_MAP_PROP = 'TEAM_MAP'; // Script Properties에 저장된 팀 키 → 문서 매핑
var LOCK_WAIT_MS = 10000; // 동시 저장 방지를 위한 락 대기 시간
var PROP_LAST_REVISION_PREFIX = 'LAST_REVISION_'; // 문서별 리비전 키 prefix
var DEFAULT_SCOPE = 'personal';
var SCOPE_PERSONAL = 'personal';
var SCOPE_TEAM = 'team';
var CATEGORY_RULES = [
  { name: 'MEETING', keywords: ['meeting', '회의', 'standup', 'sync'] },
  { name: 'BUG', keywords: ['bug', 'issue', '오류', 'error', '디버그'] },
  { name: 'FEATURE', keywords: ['feature', '기능', '스펙', 'spec'] },
  { name: 'RESEARCH', keywords: ['research', '조사', 'analysis', '분석'] },
  { name: 'HANDOFF', keywords: ['handoff', '인수인계', 'handover'] }
];

function getScriptProperties() {
  return PropertiesService.getScriptProperties();
}

function getSecret() {
  return getScriptProperties().getProperty('API_TOKEN');
}

function getPersonalDocId() {
  return getScriptProperties().getProperty('DOC_ID_PERSONAL') || DOC_ID;
}

// Script Properties에 저장된 JSON을 안전하게 객체로 변환
function getTeamMap() {
  var raw = getScriptProperties().getProperty(TEAM_MAP_PROP);
  if (!raw) return {};
  try {
    var parsed = JSON.parse(raw);
    return parsed || {};
  } catch (err) {
    return {};
  }
}

function listTeamKeys() {
  var map = getTeamMap();
  var keys = [];
  for (var key in map) {
    if (map.hasOwnProperty(key)) keys.push(key);
  }
  return keys;
}

// 사용자가 전달한 scope 파라미터를 표준화
function normalizeScope(scope) {
  var s = (scope || DEFAULT_SCOPE).toString().toLowerCase();
  if (s === SCOPE_TEAM) return SCOPE_TEAM;
  return SCOPE_PERSONAL;
}

// scope/teamKey 조합으로 실제 문서 ID를 결정
function resolveDocContext(scope, teamKey) {
  var normalizedScope = normalizeScope(scope);
  if (normalizedScope === SCOPE_PERSONAL) {
    return {
      scope: SCOPE_PERSONAL,
      teamKey: '',
      docId: getPersonalDocId()
    };
  }

  var map = getTeamMap();
  var selectedTeam = teamKey || listTeamKeys()[0] || '';
  if (!selectedTeam || !map[selectedTeam]) {
    throw new Error('UNKNOWN_TEAM');
  }
  return {
    scope: SCOPE_TEAM,
    teamKey: selectedTeam,
    docId: map[selectedTeam]
  };
}

// 문서별 리비전 키 생성
function getRevisionKey(docId) {
  return PROP_LAST_REVISION_PREFIX + (docId || 'default');
}

// 문서별 리비전 값을 확보 (없으면 새로 발급)
function ensureRevisionForDoc(docId) {
  var props = getScriptProperties();
  var revKey = getRevisionKey(docId);
  var current = props.getProperty(revKey);
  if (!current) {
    current = Utilities.getUuid();
    props.setProperty(revKey, current);
  }
  return current;
}

function bumpRevisionForDoc(docId) {
  var nextRevision = Utilities.getUuid();
  getScriptProperties().setProperty(getRevisionKey(docId), nextRevision);
  return nextRevision;
}

function formatISO(dateObj) {
  return Utilities.formatDate(dateObj || new Date(), 'UTC', "yyyy-MM-dd'T'HH:mm:ss'Z'");
}

function normalizeCategoryName(name) {
  return (name || '').toString().trim().toUpperCase();
}

// 간단한 키워드 기반 카테고리 추론
function deriveCategories(text) {
  var body = (text || '').toLowerCase();
  var categories = [];
  CATEGORY_RULES.forEach(function(rule) {
    var matched = rule.keywords.some(function(keyword) {
      return keyword && body.indexOf(keyword.toLowerCase()) !== -1;
    });
    if (matched) categories.push(rule.name);
  });
  if (!categories.length) categories.push('GENERAL');
  return categories;
}

// 블록 안의 [AUTO_CATEGORY] 라인을 파싱
function extractCategories(blockText) {
  var match = (blockText || '').match(/\[AUTO_CATEGORY\]\s*([^\n]+)/i);
  if (!match) return [];
  return match[1].split(',').map(function(item) {
    return normalizeCategoryName(item);
  }).filter(function(item) { return item; });
}

// 자동 카테고리 라인을 HANDOFF 블록에 삽입
function injectAutoCategoryLine(text, categories) {
  if (!categories || !categories.length) return text;
  if (/\[AUTO_CATEGORY\]/i.test(text)) return text;
  var catLine = '[AUTO_CATEGORY] ' + categories.join(', ');
  if (/^\s*\[HANDOFF\]/i.test(text || '')) {
    var idx = text.indexOf('\n');
    if (idx === -1) return text + '\n' + catLine;
    return text.slice(0, idx + 1) + catLine + '\n' + text.slice(idx + 1);
  }
  return catLine + '\n' + text;
}

// 문서를 '---' 구분자로 나눠 최신 블록 배열을 만듭니다.
function splitBlocks(rawText) {
  var parts = (rawText || '').split(/\n---\n/g);
  var blocks = [];
  for (var i = 0; i < parts.length; i++) {
    var trimmed = parts[i].trim();
    if (!trimmed) continue;
    blocks.push({
      text: trimmed,
      categories: extractCategories(trimmed)
    });
  }
  return blocks;
}

// 카테고리 필터가 있으면 해당 블록, 없으면 최신 블록을 선택
function selectBlock(blocks, categoryFilter) {
  if (!blocks.length) {
    return {
      block: { text: '', categories: [] },
      matchedCategory: ''
    };
  }

  var normalizedFilter = normalizeCategoryName(categoryFilter);
  if (normalizedFilter) {
    for (var i = blocks.length - 1; i >= 0; i--) {
      if (blocks[i].categories.indexOf(normalizedFilter) !== -1) {
        return {
          block: blocks[i],
          matchedCategory: normalizedFilter
        };
      }
    }
  }

  return {
    block: blocks[blocks.length - 1],
    matchedCategory: ''
  };
}

// Apps Script 이벤트에서 안전하게 파라미터 추출
function getParameter(e, key) {
  return (e && e.parameter && (e.parameter[key] || e.parameter[key.toLowerCase()])) || '';
}

function getTeamParameter(e) {
  return getParameter(e, 'team_key') || getParameter(e, 'team');
}

/**
 * [READ] GET 요청 처리 (UI 또는 JSON 데이터)
 */
function doGet(e) {
  var m = getParameter(e, 'mode') || 'ui';
  if (m === 'json') {
    var key = getParameter(e, 'key');
    if (key !== getSecret()) {
      return createJSON({ error: 'UNAUTHORIZED' });
    }
    try {
      var scope = getParameter(e, 'scope') || DEFAULT_SCOPE;
      var teamKey = getTeamParameter(e);
      var categoryFilter = getParameter(e, 'category');
      var context = resolveDocContext(scope, teamKey);
      return createJSON(getLatestAsJSON(context, categoryFilter));
    } catch (err) {
      return createJSON({ error: err.message || 'CONTEXT_ERROR' });
    }
  }

  return HtmlService.createHtmlOutputFromFile('ui')
    .setTitle('Memory Handoff Hub')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * [WRITE] POST 요청 처리
 */
function doPost(e) {
  var key = getParameter(e, 'key');
  if (key !== getSecret()) {
    return createJSON({ error: 'UNAUTHORIZED' });
  }

  var text = '';
  if (e && e.postData && e.postData.contents) text = String(e.postData.contents);
  if (!text && e && e.parameter && e.parameter.text) text = String(e.parameter.text);

  var providedRevision = getParameter(e, 'revision');
  var scope = getParameter(e, 'scope') || DEFAULT_SCOPE;
  var teamKey = getTeamParameter(e);
  var result = syncHandoff(text, providedRevision, scope, teamKey);
  return createJSON(result);
}

// ==========================================================
//  Helper Functions
// ==========================================================

function parseHandoffSections(blockText) {
  var regex = /\[([a-zA-Z0-9_ ]+)\]([\s\S]*?)(?=\n\[[a-zA-Z0-9_ ]+\]|$)/g;
  var sectionMatch;
  var parsed = {};

  if (!/^\s*\[HANDOFF\]/.test(blockText || '')) {
    parsed.content = blockText;
    return parsed;
  }

  while ((sectionMatch = regex.exec(blockText)) !== null) {
    var key = sectionMatch[1].trim();
    var value = sectionMatch[2].trim();
    if (key !== 'HANDOFF') {
      parsed[key] = value;
    }
  }
  return parsed;
}

function getLatestAsJSON(context, categoryFilter) {
  var doc = DocumentApp.openById(context.docId);
  var body = doc.getBody().getText();
  var blocks = splitBlocks(body);
  var selection = selectBlock(blocks, categoryFilter);
  var parsed = parseHandoffSections(selection.block.text);

  var meta = getDocumentMeta(context, doc);
  var result = Object.assign({}, parsed, {
    parsed_at: new Date().toISOString(),
    revision_id: meta.revisionId,
    last_updated: meta.lastUpdated,
    doc_url: meta.url,
    scope: context.scope,
    categories: selection.block.categories,
    team_key: context.teamKey || ''
  });
  if (selection.matchedCategory) {
    result.matched_category = selection.matchedCategory;
  }
  return result;
}

function appendHandoff(text, context) {
  text = (text || '').trim();
  if (!text) return { status: 'NO_TEXT' };

  var now = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm');
  var doc = DocumentApp.openById(context.docId);
  var docName = doc.getName();
  var body = doc.getBody();

  body.appendParagraph('---');
  if (!/^\s*\[HANDOFF\]/.test(text)) {
    body.appendParagraph('[HANDOFF] ' + now + ' KST');
  }

  text.split(/\r?\n/).forEach(function(line) {
    body.appendParagraph(line);
  });

  doc.saveAndClose();
  return {
    status: 'OK',
    url: 'https://docs.google.com/document/d/' + context.docId + '/edit',
    name: docName
  };
}

function getDocumentMeta(context, cachedDoc) {
  var doc = cachedDoc || DocumentApp.openById(context.docId);
  var updatedAt = doc.getLastUpdated();
  return {
    id: context.docId,
    name: doc.getName(),
    url: 'https://docs.google.com/document/d/' + context.docId + '/edit',
    lastUpdated: formatISO(updatedAt),
    revisionId: ensureRevisionForDoc(context.docId),
    scope: context.scope,
    teamKey: context.teamKey || ''
  };
}

function getDocInfo(scope, teamKey) {
  try {
    var context = resolveDocContext(scope, teamKey);
    return getDocumentMeta(context);
  } catch (err) {
    return { error: err.message || 'CONTEXT_ERROR' };
  }
}

function getTeamList() {
  var map = getTeamMap();
  var teamKeys = [];
  for (var key in map) {
    if (!map.hasOwnProperty(key)) continue;
    teamKeys.push({ key: key, docId: map[key] });
  }
  return teamKeys;
}

function createJSON(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

function syncHandoff(text, revisionId, scope, teamKey) {
  var context;
  try {
    context = resolveDocContext(scope, teamKey);
  } catch (err) {
    return { status: err.message || 'CONTEXT_ERROR' };
  }

  var currentRevision = ensureRevisionForDoc(context.docId);
  if (!revisionId) {
    return {
      status: 'MISSING_REVISION',
      revisionId: currentRevision,
      scope: context.scope,
      teamKey: context.teamKey || ''
    };
  }

  if (revisionId !== currentRevision) {
    return {
      status: 'CONFLICT',
      revisionId: currentRevision,
      providedRevision: revisionId,
      scope: context.scope,
      teamKey: context.teamKey || ''
    };
  }

  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(LOCK_WAIT_MS);
  } catch (err) {
    return {
      status: 'LOCK_TIMEOUT',
      message: '현재 다른 사용자가 저장 중입니다. 잠시 후 다시 시도하세요.',
      revisionId: currentRevision,
      scope: context.scope,
      teamKey: context.teamKey || ''
    };
  }

  var categories = deriveCategories(text);
  var preparedText = injectAutoCategoryLine(text, categories);
  var appendResult;
  try {
    appendResult = appendHandoff(preparedText, context);
    if (appendResult.status === 'OK') {
      bumpRevisionForDoc(context.docId);
    }
  } finally {
    lock.releaseLock();
  }

  var meta = getDocumentMeta(context);
  return Object.assign({}, appendResult, {
    revisionId: meta.revisionId,
    last_updated: meta.lastUpdated,
    scope: context.scope,
    teamKey: context.teamKey || '',
    categories: categories
  });
}
