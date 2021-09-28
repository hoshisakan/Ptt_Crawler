# Ptt_Crawler
## 結合 BeautifulSoup4 與 requests 之 Python 套件撈取 ptt 文章與下載其圖片

![alt text](https://imgur.com/j6pZ7kc.png)
![alt text](https://imgur.com/CxWHdEx.png)

## 教學
### 套件安裝
需要的套件已經包在 requirements.txt 的文字檔中，將此檔案放入專案路徑中，然後在終端機輸入以下指令即可
> 安裝套件之前請先確認你的環境有安裝 [Python 3.7.6](https://www.python.org/downloads/release/python-376/)
```
pip install -r requirements.txt
```

### 執行範例
* 請先建立一個 crawler.ini 的設定檔，此處拆成兩部分說明
#### 第一部分
```
Output_Path=CSV檔案與圖片的下載路徑
Base_URL=Ptt 文章的網址
Allow_Imgage_Download=是否允許下載圖片
Article_Title_Filter=過濾不想看到的文章標題
Article_Img_Type_Filter=過濾不想下載的圖片格式
Article_Img_Type_Filter_Allow=是否啟用圖片格式過濾
# 僅適用於 Keyword 模式
Page_Search_Over_Limit=是否關閉頁面搜尋的限制
```
範例如下

```
Output_Path=D:\Files\Project\Output\ptt
Base_URL=https://www.ptt.cc/bbs/Beauty/index.html
Allow_Imgage_Download=YES
Article_Title_Filter=帥哥|公告|大尺碼|肉特|選情報導|整理
Article_Img_Type_Filter=.gif
Article_Img_Type_Filter_Allow=YES
# 僅適用於 Keyword 模式
Page_Search_Over_Limit=YES
```

#### 第二部分
此程式有三種模式

* 第一種 Page 模式是撈取指定頁數的 ptt 之文章資訊

```
Action_Mode_By=Page
Article_Search_Page_Limit=10
```

* 第二種 Keyword 模式是在指定頁數範圍內撈取含有關鍵字的 ptt 之文章資訊

```
Action_Mode_By=Keyword
Article_Search_Keyword=日本
Article_Search_Page_Limit=5
```

* 第三種 Date 模式是在指定日期範圍內撈取 ptt 的文章資訊

```
Action_Mode_By=Date
Article_Search_Page_Limit=09-28
```

> 這裡以 Keyword 模式為演示範例，以關鍵字搜尋 Beauty 版上匹配的文章資訊與下載其圖片
### 執行畫面
![alt text](https://imgur.com/Pcxby0q.png)
![alt text](https://imgur.com/S3uEJKv.png)
![alt text](https://imgur.com/L8oGs34.png)

### 輸出資料夾
![alt text](https://imgur.com/pPs7h7b.png)
![alt text](https://imgur.com/yzhTtde.png)

### 輸出 csv
![alt text](https://imgur.com/rBuXcZt.png)
![alt text](https://imgur.com/uuS1lP1.png)

### 將 python 打包成一個 .exe 的可執行檔
> 打包的 python 檔是 [crawler_google_search.py](https://github.com/hoshisakan/Google_Search_Crawler/blob/main/crawler_google_search.py) 這個檔案，而非 [crawler_google_search_args.py](https://github.com/hoshisakan/Google_Search_Crawler/blob/main/crawler_google_search_args.py)，這點要特別注意
* 打包時請注意你的 python 環境是乾淨的，避免製作執行檔時將不必要的套件一同匯入，建議使用 [virtualenv](https://pypi.org/project/virtualenv/) 與 [virtualenvwrapper-win](https://pypi.org/project/virtualenvwrapper-win/) 將爬蟲的開發環境區別開來

```
pyinstaller.exe --specpath ./execute/ --distpath ./execute/dist --workpath ./execute/build --add-data "D:\Files\Project\Ptt_Crawler\crawler.ini;." -D crawler_ptt.py
```

或寫一個 shell script 執行它，這個檔案也已經放在上面，可自行參閱 [generate.sh](https://github.com/hoshisakan/Ptt_Crawler/blob/main/generate.sh)

```
#!/bin/sh
set -e

DIR="execute"
if [ -d "$DIR" ]; then
    echo "Will be remove the diretory"
    rm -rf execute
    if [ $? -eq 0 ]; then
        echo "Remove the directory successfully!"
    else
        echo "Could not remove the directory"
        exit 1
    fi
fi
pyinstaller.exe --specpath ./execute/ --distpath ./execute/dist --workpath ./execute/build --add-data "D:\Files\Project\Ptt_Crawler\crawler.ini;." -D crawler_ptt.py
```

![alt text](https://imgur.com/mfbTWRH.png)
![alt text](https://imgur.com/XCzf8WG.png)

### 執行檔打包完成後，在 dist 的目錄中會看見 crawler.ini 與 crawler_ptt.exe

![alt text](https://imgur.com/a9uAeSD.png)

* 實際測試執行檔

> 這裡以 Page 模式為演示範例，以指定的頁數搜尋 Baseball 版上匹配的文章資訊與下載其圖片
### 執行畫面
>如果該篇文章不存在任何圖片的連結，Log 輸出會以 Error 顯示該文章並不存在圖片

![alt text](https://imgur.com/L2RsFCq.png)
![alt text](https://imgur.com/3l1oELp.png)
![alt text](https://imgur.com/IE3E448.png)
![alt text](https://imgur.com/JvR9avX.png)

### 輸出資料夾
![alt text](https://imgur.com/t8ZjdBn.png)
![alt text](https://imgur.com/6OMBD2Q.png)

### 輸出 csv
![alt text](https://imgur.com/guPk2ga.png)
![alt text](https://imgur.com/kePLULX.png)
![alt text](https://imgur.com/NMVUpNF.png)

# 執行環境
* Python 3.7.6