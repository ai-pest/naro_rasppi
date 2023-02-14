var srcData = "";
var srcFileName = "";
var plant = "";
var app_ver = "";
function encode() {
  selectedfile = document.getElementById("uploadfile").files;
  if (selectedfile.length > 0) {
    imageFile = selectedfile[0];
    var fileReader = new FileReader();
    fileReader.onload = function (fileLoadedEvent) {
      srcData = fileLoadedEvent.target.result.replace(/^data:.+;base64,/, '');
    }
    srcFileName = imageFile.name;
    fileReader.readAsDataURL(imageFile);
  }
}
/*----------------------------*
 *   ファイルアップロード     *
 *----------------------------*/
(function () {
  $("#uploadSubmit").click(function () {
    var plant = document.getElementById("plant").selectedOptions[0].label;
    if (plant == '--作物を選んでください--') {
      alert('作物が選択されていません。撮影した作物を選んでください。');
      return;
    }
    var part = document.getElementById("part").selectedOptions[0].label;
    if (part == '--部位を選んでください--') {
      alert('部位が選択されていません。撮影した部位を選んでください。');
      return;
    }
    var category = document.getElementById("category").selectedOptions[0].label;
    var form = document.getElementById("fileForm");

    // 検出中はメッセージを切り替える
    $("#result").html('検出中です...');

    var formdata = new FormData(form);
    var postData = {
      "assets": [{
        "id": "data 1",
        "images": [{
          "bbox": [50, 80, 90, 150],
          "filename": srcFileName,
          "data": srcData,
          "lat": 35.00000,
          "lon": 140.00000,
          "actual": "アブラムシ"
        }],
        "attributes": {
          "category": category,
          "plant": plant,
          "part": part,
          "place": "屋内",
        }
      }]
    };
    postData.from_debug_page = true;
    var data;
    var filePath;

    // APIサーバにリクエスト送信
    $.ajax({
      url: "/wsgi",
      type: "POST",
      async: false,
      data: JSON.stringify(postData),
      processData: false,
      contentType: 'application/json',
      dataType: "json",
      success: function (json) {
        data = json;
      },
      error: function (jqXHR, textStatus, errorThrown) {
        alert("≪エラーが発生しました≫-----------------" + jqXHR.responseText);
        console.log(jqXHR.responseText);
        data = false;
      },
      timeout: 10000
    });

    // レスポンスを表示
    if (data === false) return false;
    if (data) {
      console.log("hey, it's working!");
      if (data["status"] == "error") {
        if (data["type"] == "noFile") {
          alert("ファイルを選択してください。");
          filePath = false;
        } else if (data["type"] == "badExtension") {
          alert("不正な拡張子です。")
          filePath = false;
        } else {
          alert("不明なエラーです。\n----------\n" + data["type"])
          filePath = false;
        }
        return;
      }

      var resultDiv = $("#result");

      // TODO: 「検出できない」条件は要確認
      if (data.assets[0].images[0].results.length == 0) {
        resultHtml = "<tr><td colspan=3>" + part + "を検出できませんでした。" +
          "撮影角度や距離を変えてもう一度お試しください。</td></tr>";
        resultDiv.html(resultHtml);

        return;

      } else {

        // 元画像を表示
        var resultHtml = ""
        // const originalSrc = "data:image/jpeg;base64," + srcData;
        // resultHtml += "<img width='350px' height='350px' src='" + originalSrc + "'><br/>";

        const results = data["assets"][0]["images"][0]["results"];
        // 検出した物体ごとに、検出結果、切り抜き画像、Grad-CAMを表示
        for (var i = 0; i < results.length; i++) {
          result = results[i];
          candidates = result['candidates'];

          // ヘッダを表示
          resultHtml += "<table class='detectionsTable' border='1'>"
            + "  <tr>"
            + "    <th rowspan=2>No.</th>"
            + "    <th rowspan=2>画像</th>"
            + "    <th colspan=3>検出結果</th>"
            + "  </tr>"
            + "  <tr>"
            + "    <th></th>"
            + "    <th>予測した病虫害名</th>"
            + "    <th>確信度</th>"
            + "  </tr>";

          if (candidates.length == 0) {
            // 検出結果がない場合
            resultHtml += "<tr>"
              + "  <td colspan=6>"
              + "    害虫を検出できませんでした。撮影角度や距離を変えてもう一度お試しください。"
              + "  </td>"
              + "</tr>";

          } else {
            // 検出結果がある場合 
            imageSrc = "data:image/jpeg;base64," + srcData;

            // 予測した害虫種別ごとに表示
            for (var j = 0; j < candidates.length; j++) {
              const candidate = candidates[j];
              const estimated = candidate["estimated"];   // 予測した害虫種別
              const probability = parseFloat(candidate['probability'] * 100).toFixed(1) + "%"; // 確信度（dd.f%）

              resultTr = "<tr class='resultTr'>";
              if (j == 0) {
                resultTr += "  <td class='noTd' rowspan='" + String(candidates.length) + "'>"
                  + "    " + String(i + 1)
                  + "  </td>"
                  + "  <td class='gradcamTd' rowspan='" + String(candidates.length) + "'>"
                  + "    <img class='gradcamImage' width='350px' height='350px' src='" + imageSrc + "' />"
                  + "  </td>";
              }
              resultTr += "  <td class='rankTd'>" + String(j + 1) + "</td>"
                + "  <td class='nameTd'>" + estimated + "</td>"
                + "  <td class='confidenceTd'>" + probability + "</td>"
                + "</tr>"

              resultHtml += resultTr;
            }

          }
          resultHtml += "</table>";
        }
        $("#result").html(resultHtml);
      }
    }
  });
}());
function hexToBase64(str) {
  return btoa(String.fromCharCode.apply(null, str.replace(/\\r|\\n/g, "").replace(/([\da-fA-F]{2}) ?/g, "0x$1 ").replace(/ +$/, "").split(" ")));
}
