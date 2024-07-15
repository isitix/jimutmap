*** Settings ***
Library    Browser    jsextension=${CURDIR}/module.js
Library    String
Library    isitix.py


*** Test Cases ***

Playwright Test
    Set Log Level    TRACE
    New Browser    chromium    headless=true    slowMo=3
    New Context    acceptDownloads=true
    New Page    https://satellites.pro/
    ${source}=    Get Page Source
    Log    ${source}
    #Click    //*[contains(text(),'Einwilligen')]
    Click    //*[contains(@class, 'fc-button fc-cta-consent fc-primary-button')]
    Click    //div[@id="map-canvas"]
    ${source}=    Get Page Source
    Log    ${source}
    ${dataMapPrintingBackground}=    getAccessKey
    ${accessKey}=    Get Regexp Matches    ${dataMapPrintingBackground}    \accessKey=([^&]*)\
    ${part1}=    set variable    https://sat-cdn2.apple-mapkit.com/tile?style=7&size=1&scale=1&z=19&x=390843&y=228270&v=9262&
    ${part3}=    set variable    &emphasis=standard&tint=light
    ${URL}=    set variable    ${part1}${accessKey}[0]${part3}
    Log    ${URL}
    Download    ${URL}    saveAs=${CURDIR}/tst.png

    test_KW    ${accessKey}[0]

    Take Screenshot
