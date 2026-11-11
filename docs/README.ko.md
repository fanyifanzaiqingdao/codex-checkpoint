# Codex Checkpoint

## Codex 플러그인 (권장)

이 저장소에서 아래 명령을 실행한 뒤 데스크톱 플러그인 목록에서 설치하고 활성화하세요. 대상 Git 프로젝트의 새 채팅에서 “task-checkpoint로 진행 상황 저장” 또는 “task-checkpoint로 이전 작업 계속”이라고 말하세요. pip 설치는 필요 없지만 Python 3.10+와 Git은 필요합니다. 자동 저장은 아닙니다. 지원 여부와 화면은 버전에 따라 다릅니다. 앱 내 설치 및 호출은 아직 검증하지 않았습니다.

```sh
codex plugin marketplace add .
```

코딩 도우미를 위한 로컬 작업 인계 도구입니다. Python 3.10 이상과 Git이 필요합니다.

[en](../README.md) | [zh-CN](README.zh-CN.md) | [ja](README.ja.md) | [ko](README.ko.md) | [es](README.es.md) | [fr](README.fr.md)

## 설치

```sh
python3 -m pip install .
```

## 사용법

```sh
cd /path/to/your/git-project
checkpoint init
checkpoint save --goal "Fix login" --constraint "Keep public API" --done "Found cause" --todo "Implement fix" --verified "Existing tests passed" --unverified "Browser login flow"
checkpoint status
checkpoint resume
```

저장할 때 이전 기록을 덮어씁니다. 목록 옵션은 반복할 수 있습니다. 검증 결과는 사용자가 입력하며 도구가 실행하거나 보증하지 않습니다.

```sh
checkpoint --repo /path/to/project status
```

## 개인정보 및 제한

기록은 .checkpoint/latest.json에 저장되며 Git 로컬 제외 규칙에 추가됩니다. 네트워크 통신, 채팅 읽기, 코드 수정, 자동 저장 연동은 없습니다. 공유 전에 민감한 내용을 확인하세요. Git 상태와 SHA-256으로 추적 파일과 무시되지 않은 새 파일의 변경을 감지합니다. 무시된 파일과 서브모듈 내부는 제외됩니다. 파일이 안정된 상태에서 저장하세요. resume은 새 채팅에 붙여 넣을 텍스트만 출력하며 Codex 실행이나 파일 복원은 하지 않습니다.

## 구조화된 작업 기억

Codex에 “이 작업 중 task-checkpoint로 사용자 제약, 결정 이유, 실패한 시도를 계속 기록해 주세요”라고 말하세요. 백그라운드 기능이 아니라 도우미가 중요한 시점에 호출합니다.

기록은 .checkpoint/journal.json에 ID, 종류, 생성 시간, 불변 내용, 상태 이력으로 저장됩니다. 공통 필드는 source, scope, certainty, evidence입니다. 제약은 text, 결정은 choice와 reason, 시도는 action, observed, conclusion, retry_when이 필수입니다. save는 기록을 지우지 않습니다. resume은 전체 이력을 표시하며 마지막 상태로 유효성을 판단합니다. 증거는 사용자가 제공한 설명입니다. 동시 쓰기는 재시도하세요.

```sh
checkpoint record constraint --file constraint.json
checkpoint record decision --file decision.json
checkpoint record attempt --file attempt.json
checkpoint records
checkpoint resolve RECORD_ID --status superseded --reason "Replaced by NEW_RECORD_ID"
```

```json
{
  "source": "user",
  "scope": "current release",
  "certainty": "explicit",
  "evidence": "User explicitly requested no database schema changes",
  "text": "Do not change the database schema"
}
```

## 작업과 기록

명령 앞에 --task를 지정해 작업을 분리합니다. 생략하면 기존 기본 작업입니다. 저장할 때마다 history/에 진행 상황과 당시 기록을 보관하며 자동 삭제하지 않습니다. 이전 형식의 과거 기록은 재구성할 수 없습니다. 기본 복원은 유효한 기록만 표시하고 --full은 전체 이력을 표시합니다. 과거 기록 조회는 코드나 최신 상태를 변경하지 않습니다.

```sh
checkpoint --task login init
checkpoint --task login save --goal "Fix login" --todo "Test refresh"
checkpoint --task billing init
checkpoint tasks
checkpoint --task login history
checkpoint --task login resume
checkpoint --task login resume --full
checkpoint --task login resume --checkpoint CHECKPOINT_ID
```
