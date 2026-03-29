---
name: seoul-subway
description: Seoul Subway assistant for real-time arrivals, route planning, and service alerts (Korean/English)
model: sonnet
metadata: {"moltbot":{"emoji":"","requires":{"bins":["curl","jq"]}}}
homepage: https://github.com/dukbong/seoul-subway
user-invocable: true

# Seoul Subway Skill
Query real-time Seoul Subway information. **No API key required** - uses proxy server.

## Features
Real-time Arrival, Description=Train arrival times by station, Trigger Example (KO)="강남역 도착정보", Trigger Example (EN)="Gangnam station arrivals"
Station Search, Description=Line and station code lookup, Trigger Example (KO)="강남역 몇호선?", Trigger Example (EN)="What line is Gangnam?"
Route Search, Description=Shortest path with time/fare, Trigger Example (KO)="신도림에서 서울역", Trigger Example (EN)="Sindorim to Seoul Station"
Service Alerts, Description=Delays, incidents, non-stops, Trigger Example (KO)="지하철 지연 있어?", Trigger Example (EN)="Any subway delays?"
**Last Train**, Description=Last train times by station, Trigger Example (KO)="홍대 막차 몇 시야?", Trigger Example (EN)="Last train to Hongdae?"
**Exit Info**, Description=Exit numbers for landmarks, Trigger Example (KO)="코엑스 몇 번 출구?", Trigger Example (EN)="Which exit for COEX?"
**Accessibility**, Description=Elevators, escalators, wheelchair lifts, Trigger Example (KO)="강남역 엘리베이터", Trigger Example (EN)="Gangnam elevators"
**Quick Exit**, Description=Best car for facilities, Trigger Example (KO)="강남역 빠른하차", Trigger Example (EN)="Gangnam quick exit"
**Restrooms**, Description=Restroom locations, Trigger Example (KO)="강남역 화장실", Trigger Example (EN)="Gangnam restrooms"

### Natural Language Triggers / 자연어 트리거
다양한 자연어 표현을 인식합니다:

#### Real-time Arrival / 실시간 도착
- "When's the next train at Gangnam?": "강남 몇 분 남았어?"
- "Trains at Gangnam": "강남 열차"
- "Gangnam arrivals": "강남 언제 와?"
- "Next train to Gangnam": "다음 열차 강남"

#### Route Search / 경로 검색
| "How do I get to Seoul Station from Gangnam?" | "강남에서 서울역 어떻게 가?" |
| "Gangnam → Seoul Station" | "강남 → 서울역" |
| "Gangnam to Seoul Station" | "강남에서 서울역 가는 길" |
| "Route from Gangnam to Hongdae" | "강남부터 홍대까지" |

#### Service Alerts / 운행 알림
| "Is Line 2 running normally?" | "2호선 정상 운행해?" |
| "Any delays on Line 1?" | "1호선 지연 있어?" |
| "Subway status" | "지하철 상황" |
| "Line 3 alerts" | "3호선 알림" |

#### Last Train / 막차 시간
| "Last train to Gangnam?" | "강남 막차 몇 시야?" |
| "When is the last train at Hongdae?" | "홍대입구 막차 시간" |
| "Final train to Seoul Station" | "서울역 막차" |
| "Last train on Saturday?" | "토요일 막차 시간" |

#### Exit Info / 출구 정보
| "Which exit for COEX?" | "코엑스 몇 번 출구?" |
| "Exit for Lotte World" | "롯데월드 출구" |
| "DDP which exit?" | "DDP 몇 번 출구?" |
| "Gyeongbokgung Palace exit" | "경복궁 나가는 출구" |

#### Accessibility / 접근성 정보
| "Gangnam station elevators" | "강남역 엘리베이터" |
| "Escalators at Seoul Station" | "서울역 에스컬레이터" |
| "Wheelchair lifts at Jamsil" | "잠실역 휠체어리프트" |
| "Accessibility info for Hongdae" | "홍대입구 접근성 정보" |

#### Quick Exit / 빠른하차
| "Quick exit at Gangnam" | "강남역 빠른하차" |
| "Which car for elevator?" | "엘리베이터 몇 번째 칸?" |
| "Best car for exit 3" | "3번 출구 가까운 칸" |
| "Fastest exit at Samsung" | "삼성역 빠른 하차 위치" |

#### Restrooms / 화장실
| "Restrooms at Gangnam" | "강남역 화장실" |
| "Where's the bathroom at Myeongdong?" | "명동역 화장실 어디야?" |
| "Accessible restroom at Seoul Station" | "서울역 장애인 화장실" |
| "Baby changing station at Jamsil" | "잠실역 기저귀 교환대" |

## First Time Setup / 첫 사용 안내
When you first use this skill, you'll see a permission prompt for the proxy domain.

처음 사용 시 프록시 도메인 접근 확인 창이 뜹니다.

**Select / 선택:** `Yes, and don't ask again for vercel-proxy-henna-eight.vercel.app`

This only needs to be done once. / 한 번만 하면 됩니다.

## Proxy API Reference
All API calls go through the proxy server. No API keys needed for users.

### Base URL
```
https://vercel-proxy-henna-eight.vercel.app

### 1. Real-time Arrival Info
**Endpoint**
GET /api/realtime/{station}?start=0&end=10

**Parameters**

station, Required=Yes, Description=Station name (Korean, URL-encoded)
start, Required=No, Description=Start index (default: 0)
end, Required=No, Description=End index (default: 10)
format, Required=No, Description=`formatted` (markdown, default) or `raw` (JSON)
lang, Required=No, Description=`ko` (default) or `en`

**Response Fields**

- `subwayId`: Line ID (1002=Line 2, 1077=Sinbundang)
- `trainLineNm`: Direction (e.g., "성수행 - 역삼방면")
- `arvlMsg2`: Arrival time (e.g., "4분 20초 후")
- `arvlMsg3`: Current location
- `isFastTrain`: Fast train flag (1=급행)

**Example**
```bash
curl "https://vercel-proxy-henna-eight.vercel.app/api/realtime/강남"

### 2. Station Search
GET /api/stations?station={name}&start=1&end=10

| station | Yes | Station name to search |
| start | No | Start index (default: 1) |

| `STATION_CD` | Station code |
| `STATION_NM` | Station name |
| `LINE_NUM` | Line name (e.g., "02호선") |
| `FR_CODE` | External station code |

curl "https://vercel-proxy-henna-eight.vercel.app/api/stations?station=강남"

### 3. Route Search
GET /api/route?dptreStnNm={departure}&arvlStnNm={arrival}

| dptreStnNm | Yes | Departure station |
| arvlStnNm | Yes | Arrival station |
| searchDt | No | Datetime (yyyy-MM-dd HH:mm:ss) |
| searchType | No | duration / distance / transfer |

| `totalDstc` | Total distance (m) |
| `totalreqHr` | Total time (seconds) |
| `totalCardCrg` | Fare (KRW) |
| `paths[].trainno` | Train number |
| `paths[].trainDptreTm` | Departure time |
| `paths[].trainArvlTm` | Arrival time |
| `paths[].trsitYn` | Transfer flag |

curl "https://vercel-proxy-henna-eight.vercel.app/api/route?dptreStnNm=신도림&arvlStnNm=서울역"

### 4. Service Alerts
GET /api/alerts?pageNo=1&numOfRows=10&format=enhanced

| pageNo | No | Page number (default: 1) |
| numOfRows | No | Results per page (default: 10) |
| lineNm | No | Filter by line |
| format | No | `default` or `enhanced` (structured response) |

**Response Fields (Default)**

| `ntceNo` | Notice number |
| `ntceSj` | Notice title |
| `ntceCn` | Notice content |
| `lineNm` | Line name |
| `regDt` | Registration date |

**Response Fields (Enhanced)**

| `summary.delayedLines` | Lines with delays |
| `summary.suspendedLines` | Lines with service suspended |
| `summary.normalLines` | Lines operating normally |
| `alerts[].lineName` | Line name (Korean) |
| `alerts[].lineNameEn` | Line name (English) |
| `alerts[].status` | `normal`, `delayed`, or `suspended` |
| `alerts[].severity` | `low`, `medium`, or `high` |
| `alerts[].title` | Alert title |

# Default format
curl "https://vercel-proxy-henna-eight.vercel.app/api/alerts"

# Enhanced format with status summary
curl "https://vercel-proxy-henna-eight.vercel.app/api/alerts?format=enhanced"

### 5. Last Train Time
> **참고:** 이 API는 주요 역 77개의 막차 시간을 정적 데이터로 제공합니다.
> 서울교통공사 2025년 1월 기준 데이터입니다.
>
> **지원 역 (77개):**
> 가산디지털단지, 강남, 강남구청, 강변, 건대입구, 경복궁, 고속터미널, 공덕, 광나루, 광화문, 교대, 구로, 군자, 김포공항, 노량진, 당산, 대림, 동대문, 동대문역사문화공원, 디지털미디어시티, 뚝섬, 마포구청, 명동, 모란, 몽촌토성, 복정, 불광, 사가정, 사당, 삼각지, 삼성, 상봉, 서울대입구, 서울역, 선릉, 성수, 수유, 시청, 신논현, 신당, 신도림, 신사, 신촌, 안국, 압구정, 약수, 양재, 여의도, 역삼, 연신내, 영등포, 옥수, 올림픽공원, 왕십리, 용산, 을지로3가, 을지로4가, 을지로입구, 응암, 이대, 이촌, 이태원, 인천공항1터미널, 인천공항2터미널, 잠실, 정자, 종각, 종로3가, 종합운동장, 천호, 청담, 충무로, 판교, 합정, 혜화, 홍대입구, 효창공원앞

GET /api/last-train/{station}?direction=up&weekType=1

| station | Yes | Station name (Korean or English) |
| direction | No | `up`, `down`, or `all` (default: all) |
| weekType | No | `1`=Weekday, `2`=Saturday, `3`=Sunday/Holiday (default: auto) |

| `station` | Station name (Korean) |
| `stationEn` | Station name (English) |
| `lastTrains[].direction` | Direction (Korean) |
| `lastTrains[].directionEn` | Direction (English) |
| `lastTrains[].time` | Last train time (HH:MM) |
| `lastTrains[].weekType` | Day type (Korean) |
| `lastTrains[].weekTypeEn` | Day type (English) |
| `lastTrains[].line` | Line name |
| `lastTrains[].lineEn` | Line name (English) |
| `lastTrains[].destination` | Final destination |
| `lastTrains[].destinationEn` | Destination (English) |

# Auto-detect day type
curl "https://vercel-proxy-henna-eight.vercel.app/api/last-train/홍대입구"

# English station name
curl "https://vercel-proxy-henna-eight.vercel.app/api/last-train/Hongdae"

# Specific direction and day
curl "https://vercel-proxy-henna-eight.vercel.app/api/last-train/강남?direction=up&weekType=1"

### 6. Exit Information
> **참고:** 이 API는 주요 역 77개의 출구 정보를 정적 데이터로 제공합니다.

GET /api/exits/{station}

**Error Response (Unsupported Station)**

```json
{
 "code": "INVALID_STATION",
 "message": "Exit information not available for this station",
 "hint": "Exit information is available for major tourist stations only"
}

| `line` | Line name |
| `exits[].number` | Exit number |
| `exits[].landmark` | Nearby landmark (Korean) |
| `exits[].landmarkEn` | Nearby landmark (English) |
| `exits[].distance` | Walking distance |
| `exits[].facilities` | Facility types |

# Get COEX exit info
curl "https://vercel-proxy-henna-eight.vercel.app/api/exits/삼성"

curl "https://vercel-proxy-henna-eight.vercel.app/api/exits/Samsung"

### 7. Accessibility Info
GET /api/accessibility/{station}

| type | No | `elevator`, `escalator`, `wheelchair`, or `all` (default: all) |

| `elevators[].lineNm` | Line name |
| `elevators[].dtlPstn` | Detailed location |
| `elevators[].bgngFlr` / `endFlr` | Floor level (start/end) |
| `elevators[].bgngFlrGrndUdgdSe` | Ground/underground (지상/지하) |
| `elevators[].oprtngSitu` | Operation status (M=normal) |
| `escalators[]` | Same structure as elevators |
| `wheelchairLifts[]` | Same structure as elevators |

# All accessibility info
curl "https://vercel-proxy-henna-eight.vercel.app/api/accessibility/강남"

# Elevators only
curl "https://vercel-proxy-henna-eight.vercel.app/api/accessibility/강남?type=elevator"

# English output
curl "https://vercel-proxy-henna-eight.vercel.app/api/accessibility/Gangnam?lang=en"

# Raw JSON
curl "https://vercel-proxy-henna-eight.vercel.app/api/accessibility/강남?format=raw"

### 8. Quick Exit Info
GET /api/quick-exit/{station}

| facility | No | `elevator`, `escalator`, `exit`, or `all` (default: all) |

| `quickExits[].lineNm` | Line name |
| `quickExits[].drtnInfo` | Direction |
| `quickExits[].qckgffVhclDoorNo` | Best car/door number |
| `quickExits[].plfmCmgFac` | Facility type (엘리베이터/계단/에스컬레이터) |
| `quickExits[].upbdnbSe` | Up/down direction (상행/하행) |
| `quickExits[].elvtrNo` | Elevator number (if applicable) |

# All quick exit info
curl "https://vercel-proxy-henna-eight.vercel.app/api/quick-exit/강남"

# Filter by elevator
curl "https://vercel-proxy-henna-eight.vercel.app/api/quick-exit/강남?facility=elevator"

curl "https://vercel-proxy-henna-eight.vercel.app/api/quick-exit/Gangnam"

### 9. Restroom Info
GET /api/restrooms/{station}

| `restrooms[].lineNm` | Line name |
| `restrooms[].dtlPstn` | Detailed location |
| `restrooms[].stnFlr` | Floor level (e.g., B1) |
| `restrooms[].grndUdgdSe` | Ground/underground (지상/지하) |
| `restrooms[].gateInoutSe` | Inside/outside gate (내부/외부) |
| `restrooms[].rstrmInfo` | Restroom type info |
| `restrooms[].whlchrAcsPsbltyYn` | Wheelchair accessible (Y/N) |

# Get restroom info
curl "https://vercel-proxy-henna-eight.vercel.app/api/restrooms/강남"

curl "https://vercel-proxy-henna-eight.vercel.app/api/restrooms/Gangnam?lang=en"

curl "https://vercel-proxy-henna-eight.vercel.app/api/restrooms/강남?format=raw"

## Landmark → Station Mapping
외국인 관광객이 자주 찾는 랜드마크와 해당 역 정보입니다.

COEX / 코엑스, Station=삼성 Samsung, Line=2호선, Exit=5-6
Lotte World / 롯데월드, Station=잠실 Jamsil, Line=2호선, Exit=4
Lotte World Tower, Station=잠실 Jamsil, Line=2호선, Exit=3
Gyeongbokgung Palace / 경복궁, Station=경복궁 Gyeongbokgung, Line=3호선, Exit=5
Changdeokgung Palace / 창덕궁, Station=안국 Anguk, Line=3호선, Exit=3
DDP / 동대문디자인플라자, Station=동대문역사문화공원, Line=2호선, Exit=1
Myeongdong / 명동, Station=명동 Myeongdong, Line=4호선, Exit=6
N Seoul Tower / 남산타워, Station=명동 Myeongdong, Line=4호선, Exit=3
Bukchon Hanok Village, Station=안국 Anguk, Line=3호선, Exit=6
Insadong / 인사동, Station=안국 Anguk, Line=3호선, Exit=1
Hongdae / 홍대, Station=홍대입구 Hongik Univ., Line=2호선, Exit=9
Itaewon / 이태원, Station=이태원 Itaewon, Line=6호선, Exit=1
Gangnam / 강남, Station=강남 Gangnam, Line=2호선, Exit=10-11
Yeouido Park / 여의도공원, Station=여의도 Yeouido, Line=5호선, Exit=5
IFC Mall, Station=여의도 Yeouido, Line=5호선, Exit=1
63 Building, Station=여의도 Yeouido, Line=5호선, Exit=3
Gwanghwamun Square / 광화문광장, Station=광화문 Gwanghwamun, Line=5호선, Exit=2
Namdaemun Market / 남대문시장, Station=서울역 Seoul Station, Line=1호선, Exit=10
Cheonggyecheon Stream / 청계천, Station=을지로입구 Euljiro 1-ga, Line=2호선, Exit=6
Express Bus Terminal, Station=고속터미널 Express Terminal, Line=3호선, Exit=4,8
Gimpo Airport, Station=김포공항 Gimpo Airport, Line=5호선, Exit=1,3
Incheon Airport T1, Station=인천공항1터미널, Line=공항철도, Exit=1
Incheon Airport T2, Station=인천공항2터미널, Line=공항철도, Exit=1

## Static Data (GitHub Raw)
For static data like station lists and line mappings, use GitHub raw URLs:

# Station list
curl "https://raw.githubusercontent.com/dukbong/seoul-subway/main/data/stations.json"

# Line ID mappings
curl "https://raw.githubusercontent.com/dukbong/seoul-subway/main/data/lines.json"

# Station name translations
curl "https://raw.githubusercontent.com/dukbong/seoul-subway/main/data/station-names.json"

## Line ID Mapping
Line 1, ID=1001, Line=Line 6, ID=1006
Line 2, ID=1002, Line=Line 7, ID=1007
Line 3, ID=1003, Line=Line 8, ID=1008
Line 4, ID=1004, Line=Line 9, ID=1009
Line 5, ID=1005, Line=Sinbundang, ID=1077
Gyeongui-Jungang, ID=1063, Line=Gyeongchun, ID=1067
Airport Railroad, ID=1065, Line=Suin-Bundang, ID=1075

## Station Name Mapping (English → Korean)
주요 역 이름의 영어-한글 매핑 테이블입니다. API 호출 시 영어 입력을 한글로 변환해야 합니다.

### Line 1 (1호선)
Seoul Station, Korean=서울역, English=City Hall, Korean=시청
Jonggak, Korean=종각, English=Jongno 3-ga, Korean=종로3가
Jongno 5-ga, Korean=종로5가, English=Dongdaemun, Korean=동대문
Cheongnyangni, Korean=청량리, English=Yongsan, Korean=용산
Noryangjin, Korean=노량진, English=Yeongdeungpo, Korean=영등포
Guro, Korean=구로, English=Incheon, Korean=인천
Bupyeong, Korean=부평, English=Suwon, Korean=수원

### Line 2 (2호선)
| Gangnam | 강남 | Yeoksam | 역삼 |
| Samseong | 삼성 | Jamsil | 잠실 |
| Sindorim | 신도림 | Hongdae (Hongik Univ.) | 홍대입구 |
| Hapjeong | 합정 | Dangsan | 당산 |
| Yeouido | 여의도 | Konkuk Univ. | 건대입구 |
| Seolleung | 선릉 | Samsung | 삼성 |
| Sports Complex | 종합운동장 | Gangbyeon | 강변 |
| Ttukseom | 뚝섬 | Seongsu | 성수 |
| Wangsimni | 왕십리 | Euljiro 3-ga | 을지로3가 |
| Euljiro 1-ga | 을지로입구 | City Hall | 시청 |
| Chungjeongno | 충정로 | Ewha Womans Univ. | 이대 |
| Sinchon | 신촌 | Sadang | 사당 |
| Nakseongdae | 낙성대 | Seoul Nat'l Univ. | 서울대입구 |
| Guro Digital Complex | 구로디지털단지 | Mullae | 문래 |

### Line 3 (3호선)
| Gyeongbokgung | 경복궁 | Anguk | 안국 |
| Jongno 3-ga | 종로3가 | Chungmuro | 충무로 |
| Dongguk Univ. | 동대입구 | Yaksu | 약수 |
| Apgujeong | 압구정 | Sinsa | 신사 |
| Express Bus Terminal | 고속터미널 | Gyodae | 교대 |
| Nambu Bus Terminal | 남부터미널 | Yangjae | 양재 |
| Daehwa | 대화 | Juyeop | 주엽 |

### Line 4 (4호선)
| Myeongdong | 명동 | Hoehyeon | 회현 |
| Seoul Station | 서울역 | Sookmyung Women's Univ. | 숙대입구 |
| Dongdaemun History & Culture Park | 동대문역사문화공원 | Hyehwa | 혜화 |
| Hansung Univ. | 한성대입구 | Mia | 미아 |
| Mia Sageori | 미아사거리 | Gireum | 길음 |
| Chongshin Univ. | 총신대입구 | Sadang | 사당 |

### Line 5 (5호선)
| Gwanghwamun | 광화문 | Jongno 3-ga | 종로3가 |
| Dongdaemun History & Culture Park | 동대문역사문화공원 | Cheonggu | 청구 |
| Wangsimni | 왕십리 | Haengdang | 행당 |
| Yeouido | 여의도 | Yeouinaru | 여의나루 |
| Mapo | 마포 | Gongdeok | 공덕 |
| Gimpo Airport | 김포공항 | Banghwa | 방화 |

### Line 6 (6호선)
| Itaewon | 이태원 | Samgakji | 삼각지 |
| Noksapyeong | 녹사평 | Hangang | 한강진 |
| Sangsu | 상수 | Hapjeong | 합정 |
| World Cup Stadium | 월드컵경기장 | Digital Media City | 디지털미디어시티 |

### Line 7 (7호선)
| Gangnam-gu Office | 강남구청 | Cheongdam | 청담 |
| Konkuk Univ. | 건대입구 | Children's Grand Park | 어린이대공원 |
| Junggok | 중곡 | Ttukseom Resort | 뚝섬유원지 |
| Express Bus Terminal | 고속터미널 | Nonhyeon | 논현 |
| Hakdong | 학동 | Bogwang | 보광 |
| Jangam | 장암 | Dobongsan | 도봉산 |

### Line 8 (8호선)
| Jamsil | 잠실 | Mongchontoseong | 몽촌토성 |
| Gangdong-gu Office | 강동구청 | Cheonho | 천호 |
| Bokjeong | 복정 | Sanseong | 산성 |
| Moran | 모란 | Amsa | 암사 |

### Line 9 (9호선)
| Sinnonhyeon | 신논현 | Express Bus Terminal | 고속터미널 |
| Dongjak | 동작 | Noryangjin | 노량진 |
| Yeouido | 여의도 | National Assembly | 국회의사당 |
| Dangsan | 당산 | Yeomchang | 염창 |
| Gimpo Airport | 김포공항 | Gaehwa | 개화 |
| Olympic Park | 올림픽공원 | Sports Complex | 종합운동장 |

### Sinbundang Line (신분당선)
| Gangnam | 강남 | Sinsa | 신사 |
| Yangjae | 양재 | Yangjae Citizen's Forest | 양재시민의숲 |
| Pangyo | 판교 | Jeongja | 정자 |
| Dongcheon | 동천 | Suji District Office | 수지구청 |
| Gwanggyo | 광교 | Gwanggyo Jungang | 광교중앙 |

### Gyeongui-Jungang Line (경의중앙선)
| Seoul Station | 서울역 | Hongdae (Hongik Univ.) | 홍대입구 |
| Gongdeok | 공덕 | Hyochang Park | 효창공원앞 |
| Yongsan | 용산 | Oksu | 옥수 |
| Wangsimni | 왕십리 | Cheongnyangni | 청량리 |
| DMC | 디지털미디어시티 | Susaek | 수색 |
| Ilsan | 일산 | Paju | 파주 |

### Airport Railroad (공항철도)
| Seoul Station | 서울역 | Gongdeok | 공덕 |
| Hongdae (Hongik Univ.) | 홍대입구 | Digital Media City | 디지털미디어시티 |
| Gimpo Airport | 김포공항 | Incheon Airport T1 | 인천공항1터미널 |
| Incheon Airport T2 | 인천공항2터미널 | Cheongna Int'l City | 청라국제도시 |

### Suin-Bundang Line (수인분당선)
| Wangsimni | 왕십리 | Seolleung | 선릉 |
| Gangnam-gu Office | 강남구청 | Seonjeongneung | 선정릉 |
| Jeongja | 정자 | Migeum | 미금 |
| Ori | 오리 | Jukjeon | 죽전 |
| Suwon | 수원 | Incheon | 인천 |

## Usage Examples
**Real-time Arrival**

**Station Search**

**Route Search**

**Service Alerts**

# Enhanced format with delay summary
**Last Train**

# Korean station name
curl "https://vercel-proxy-henna-eight.vercel.app/api/last-train/Gangnam"

**Exit Information**

# For Lotte World
curl "https://vercel-proxy-henna-eight.vercel.app/api/exits/잠실"

**Accessibility**

**Quick Exit**

# Quick exit for elevators
**Restrooms**

# Restroom locations

## Line Color Mapping / 노선 색상 매핑
1호선 / Line 1, Color / 색상=Blue / 파랑, Emoji=
2호선 / Line 2, Color / 색상=Green / 초록, Emoji=🟢
3호선 / Line 3, Color / 색상=Orange / 주황, Emoji=🟠
4호선 / Line 4, Color / 색상=Sky Blue / 하늘, Emoji=
5호선 / Line 5, Color / 색상=Purple / 보라, Emoji=🟣
6호선 / Line 6, Color / 색상=Brown / 갈색, Emoji=🟤
7호선 / Line 7, Color / 색상=Olive / 올리브, Emoji=🟢
8호선 / Line 8, Color / 색상=Pink / 분홍, Emoji=
9호선 / Line 9, Color / 색상=Gold / 금색, Emoji=🟡
신분당선 / Sinbundang, Color / 색상=Red / 빨강, Emoji=
경의중앙선 / Gyeongui-Jungang, Color / 색상=Cyan / 청록, Emoji=
공항철도 / Airport Railroad, Color / 색상=Blue / 파랑, Emoji=
수인분당선 / Suin-Bundang, Color / 색상=Yellow / 노랑, Emoji=🟡

## Output Format Guide

### Real-time Arrival
**Korean:**
[강남역 Gangnam]

| 🟢 2 | 성수 (Seongsu) | 3분 | 역삼 | 일반 |
| 🟢 2 | 신촌 (Sinchon) | 5분 | 선정릉 | 일반 |

**English:**
[Gangnam Station 강남역]

| 🟢 2 | Seongsu (성수) | 3 min | Yeoksam | Regular |
| 🟢 2 | Sinchon (신촌) | 5 min | Seonjeongneung | Regular |

### Station Search
[강남역]

2호선, 역코드=222, 외부코드=0222

[Gangnam Station]

Line 2, Station Code=222, External Code=0222

### Route Search
[강남 → 홍대입구]

소요시간: 38분 | 거리: 22.1km | 요금: 1,650원 | 환승: 1회

🟢 강남 ─2호선─▶ 🟢 신도림 ─2호선─▶ 🟢 홍대입구

출발, 역=강남 Gangnam, 호선=🟢 2, 시간=09:03
환승, 역=신도림 Sindorim, 호선=🟢 2→2, 시간=09:18
도착, 역=홍대입구 Hongdae, 호선=🟢 2, 시간=09:42

[Gangnam → Hongdae]

Time: 38 min | Distance: 22.1 km | Fare: 1,650 KRW | Transfer: 1

🟢 Gangnam ─Line 2─▶ 🟢 Sindorim ─Line 2─▶ 🟢 Hongdae

Depart, Station=Gangnam 강남, Line=🟢 2, Time=09:03
Transfer, Station=Sindorim 신도림, Line=🟢 2→2, Time=09:18
Arrive, Station=Hongdae 홍대입구, Line=🟢 2, Time=09:42

### Service Alerts
[운행 알림]

 1호선 | 종로3가역 무정차 (15:00 ~ 15:22)
└─ 코레일 열차 연기 발생으로 인함

🟢 2호선 | 정상 운행

[Service Alerts]

 Line 1 | Jongno 3-ga Non-stop (15:00 ~ 15:22)
└─ Due to smoke from Korail train

🟢 Line 2 | Normal operation

### Last Train
[홍대입구 막차 시간]

🟢 내선순환, 시간=00:32, 종착역=성수, 요일=평일
🟢 외선순환, 시간=00:25, 종착역=신도림, 요일=평일

[Last Train - Hongik Univ.]

🟢 Inner Circle, Time=00:32, Destination=Seongsu, Day=Weekday
🟢 Outer Circle, Time=00:25, Destination=Sindorim, Day=Weekday

### Exit Info
[삼성역 출구 정보]

5번, 시설=코엑스몰, 거리=도보 3분
6번, 시설=코엑스 아쿠아리움, 거리=도보 5분
7번, 시설=봉은사, 거리=도보 10분

[Samsung Station Exits]

#5, Landmark=COEX Mall, Distance=3 min walk
#6, Landmark=COEX Aquarium, Distance=5 min walk
#7, Landmark=Bongeunsa Temple, Distance=10 min walk

### Accessibility Info
[강남역 접근성 정보 Gangnam]

### 엘리베이터
2호선, 위치=대합실, 층=지하 B1, 구분=일반
신분당선, 위치=개찰구, 층=지하 B2, 구분=일반

**운영 현황**

1, 위치=대합실, 상태=🟢 정상, 운영시간=05:30 ~ 24:00

### ↗️ 에스컬레이터
| 2호선 | 출구 1 | 지하 B1 | 상행 |

### 휠체어리프트
2호선, 번호=1, 위치=3번 출구, 상태=🟢 정상

[Gangnam Station Accessibility 강남역]

### Elevators
Line 2, Location=Concourse, Floor=Underground B1, Type=General

### ↗️ Escalators
| Line 2 | Exit 1 | Underground B1 | Up |

### Wheelchair Lifts
Line 2, No.=1, Location=Exit 3, Status=🟢 Normal

### Quick Exit
[강남역 빠른하차 정보 Gangnam]

| 2호선 | 외선 | 3-2 | 1 | 1 | 1 | 1 |
| 2호선 | 내선 | 7-1 | 5 | 2 | 2 | 2 |

[Gangnam Station Quick Exit 강남역]

| Line 2 | Outer | 3-2 | 1 | 1 | 1 | 1 |
| Line 2 | Inner | 7-1 | 5 | 2 | 2 | 2 |

### Restrooms
[강남역 화장실 정보 Gangnam]

| 2호선 | 대합실 | 지하 B1 | 개찰구 내 | 일반 | 남 3 (소 5) 여 5 1 | 있음 |
| 2호선 | 출구1 | 지하 B1 | 개찰구 외 | 일반 | 남 2 (소 3) 여 3 | 없음 |

**요약:** 총 2개 | 개찰구 내 1개 | 개찰구 외 1개 | 장애인화장실 1개 | 기저귀교환대 있음

[Gangnam Station Restrooms 강남역]

| Line 2 | Concourse | Under B1 | Inside gate | General | M:3 (U:5) W:5 :1 | Yes |
| Line 2 | Exit 1 | Under B1 | Outside gate | General | M:2 (U:3) W:3 | No |

**Summary:** Total 2 | Inside gate: 1 | Outside gate: 1 | Accessible: 1 | Baby station: Yes

### Error
오류: 역을 찾을 수 없습니다.
"강남" (역 이름만)으로 검색해 보세요.

Error: Station not found.
Try searching with "Gangnam" (station name only).