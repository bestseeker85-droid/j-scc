/**
 * J-SCC 참여 신청 Google Form 자동 생성 스크립트 (2026-09-13 개정: 4분야 체계·세부 관심·참여 형태·고등학생)
 * 사용법: script.google.com → 새 프로젝트 → 이 코드 붙여넣기 → createJsccForm 실행(권한 승인) → 실행 로그의 주소 확인
 *  - "편집 URL": 폼 수정용
 *  - "삽입 URL": 사이트 apply.html / en/apply.html 의 GOOGLE_FORM_EMBED_URL 자리에 넣을 주소
 *  - 응답은 자동으로 만들어지는 Google Sheets 에 쌓입니다.
 */
function createJsccForm() {
  var form = FormApp.create('J-SCC 참여 신청 / Application');
  form.setDescription(
    '제주형 반도체 융합센터(J-SCC) 교육과정·프로그램 참여 신청 및 문의.\n' +
    'Application and inquiries for J-SCC (Jeju Silicon Convergence Center) courses and programs.\n\n' +
    '제출된 정보는 교육과정 안내와 선발에만 사용합니다. / Your information is used only for course guidance and selection.'
  );
  form.setCollectEmail(false);
  form.setLimitOneResponsePerUser(false);
  form.setConfirmationMessage('신청이 접수되었습니다. 담당자가 이메일로 안내드리겠습니다.\nYour application has been received. We will contact you by email.');

  form.addMultipleChoiceItem()
    .setTitle('구분 / Category')
    .setChoiceValues(['제주대 전자공학과 학생 / JNU electronics student', '제주대 타 학과 학생 / JNU student, other department',
                      '타 대학 학생 / Student at another university', '대학원생 / Graduate student', '유학생 / International student',
                      '재직자 / Working engineer', '고등학생·교사 / High-school student or teacher', '기업·기관 / Company or institution'])
    .setRequired(true);

  form.addTextItem().setTitle('이름 / Name').setRequired(true);
  form.addTextItem().setTitle('소속 (학교·학과·회사) / Affiliation').setRequired(true);

  var email = form.addTextItem().setTitle('이메일 / Email').setRequired(true);
  email.setValidation(FormApp.createTextValidation().requireTextIsEmail().setHelpText('올바른 이메일 주소를 입력하세요 / Enter a valid email').build());

  form.addCheckboxItem()
    .setTitle('관심 분야 (복수 선택) / Fields of interest')
    .setHelpText('반도체 전주기 기준 네 분야입니다. / The four fields along the semiconductor cycle.')
    .setChoiceValues(['① 소자 설계·공정 / Device design & process', '② 회로 설계·제작 / Circuit design & fabrication',
                      '③ 시스템 설계 / System design', '④ 검증·측정 / Test & measurement', '아직 모름·전반적으로 알고 싶음 / Not sure yet, general interest'])
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('세부 관심 (선택) / Specific topics (optional)')
    .setChoiceValues(['TCAD 소자 시뮬레이션 / TCAD device simulation', '공정 실습(fab) / Fab practice',
                      '아날로그·혼성 회로 / Analog & mixed-signal circuits', 'RF 회로 / RF circuits', '레이아웃·Tape-out / Layout & tape-out',
                      '디지털 설계·Verilog / Digital design & Verilog', 'FPGA', 'RISC-V·SoC', 'AI 가속기 / AI accelerators',
                      '계측 기초(오실로스코프 등) / Basic instruments', '칩 측정(프로브 스테이션) / Chip probing',
                      '패키징·와이어 본딩 / Packaging & wire bonding', '모듈·보드 제작 / Module & board build']);

  form.addMultipleChoiceItem()
    .setTitle('참여 형태 / How you want to take part')
    .setChoiceValues(['정규 과정(기초 → 실무) / Regular track', '단기·체험(특강·캠프) / Short course or camp',
                      '재직자 과정 / Working-engineer course', '기업·기관 협력 / Company or institution collaboration', '아직 모름 / Not sure yet']);

  form.addParagraphTextItem().setTitle('문의 내용 / Message');

  form.addCheckboxItem()
    .setTitle('개인정보 수집·이용 동의 (필수) / Consent to collection and use of personal data (required)')
    .setHelpText('수집 항목: 이름·소속·이메일 · 목적: 교육과정 안내·선발 · 보유기간: 사업 종료(2030년 2월 예정) 후 1년 · 동의를 거부할 수 있으나 거부 시 신청이 제한됩니다. 문의: sylee@jejunu.ac.kr\n' +
                 'Items: name, affiliation, email · Purpose: course guidance and selection · Retention: one year after the project ends (planned for February 2030). Contact: sylee@jejunu.ac.kr')
    .setChoiceValues(['동의합니다 / I agree'])
    .setRequired(true);

  var ss = SpreadsheetApp.create('J-SCC 참여 신청 응답');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  var pub = form.getPublishedUrl();
  var embed = pub.replace('/viewform', '/viewform?embedded=true');
  Logger.log('편집 URL: ' + form.getEditUrl());
  Logger.log('공개 URL: ' + pub);
  Logger.log('삽입 URL (사이트에 넣을 주소): ' + embed);
  Logger.log('응답 시트: ' + ss.getUrl());
}
