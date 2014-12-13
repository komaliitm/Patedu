'use strict';
(function() {
  var app = angular.module('MainApp', ['ngRoute', 'infinite-scroll'], function($interpolateProvider) {
    $interpolateProvider.startSymbol('#{');
    $interpolateProvider.endSymbol('}#');
  });

  app.controller('DasboardController', ['$scope', 'dashboardService',
    function($scope, dashboardService) {
      $scope.dashboardParams = {
        since_months: 1,
        blockid: ""
      }

      $scope.RefreshDataFromServer = function($event, type){
        fetchDataCurrent();
      }
      $scope.Asc =0; 
      $scope.SerialNum=0;
      $scope.dashdata = null;
      fetchDataCurrent();

    $scope.SortData = function($event, type) {
        //Sort the dashdata according to type
        if($scope.SerialNum == type)
        {
            $scope.Asc > 0 ? $scope.Asc =0 : $scope.Asc =1;
        }
        else
          $scope.Asc =0;

        $scope.dashdata.data.sort(function(a, b) {
            var keyA;var keyB;
            if (type == 1) {
                keyA = a.status;
                keyB = b.status;
            }
            else if (type == 2) {
                var str1 = a.Subcenter;
                var str2 = b.Subcenter;
          console.log(str1+ " " + str2);
            str1.toLowerCase()>str2.toLowerCase()?console.log(" a>b "):console.log(" a<b ")

             if ($scope.Asc == 1) {
                if (str1.toLowerCase() > str2.toLowerCase()) return -1;
                if (str2.toLowerCase() > str1.toLowerCase()) return 1;
            } else {
                if (str1.toLowerCase() < str2.toLowerCase()) return -1;
                if (str2.toLowerCase() < str1.toLowerCase()) return 1;
            }
            }
            else if (type == 3) {
                keyA = a.Beneficiaries_anc + a.Beneficiaries_pnc + a.Beneficiaries_imm;
                keyB = b.Beneficiaries_anc + b.Beneficiaries_pnc + b.Beneficiaries_imm;
            }
            else if (type == 4) {
                keyA = a.new_reg_anc + a.new_reg_pnc  + a.new_reg_imm;
                keyB = b.new_reg_anc + b.new_reg_pnc  + b.new_reg_imm;
            }
            else if (type == 5) {
                keyA = a.GivenServices_anc + a.GivenServices_pnc + a.GivenServices_imm;
                keyB = b.GivenServices_anc + b.GivenServices_pnc + b.GivenServices_imm;
            }
            else if (type == 6) {
                keyA = a.Overdue_anc + a.Overdue_pnc + a.Overdue_imm;
                keyB = b.Overdue_anc + b.Overdue_pnc + b.Overdue_imm;
            }
            else {
                keyA = a.OverDueRate_imm +  a.OverDueRate_pnc  + a.OverDueRate_anc;
                keyB = b.OverDueRate_imm +  b.OverDueRate_pnc  + b.OverDueRate_anc;
            }
            if ($scope.Asc == 1) {
                if (keyA < keyB) return -1;
                if (keyA > keyB) return 1;
            } else {
                if (keyA > keyB) return -1;
                if (keyA < keyB) return 1;
            }
            return 0;
        });

        $scope.SerialNum= type;

    }


      function fetchDataCurrent() {
        dashboardService.getDashboardData($scope.dashboardParams).then(function(dashdata) {
          $scope.dashdata = dashdata;
          DrawPieChart($scope.dashdata.summary.Good, $scope.dashdata.summary.Average, $scope.dashdata.summary.Poor);
          PoplatePoints($scope.dashdata.data);
          console.log($scope.dashdata);
        });
      }
    }
  ]);

  app.factory('dashboardService', function($http, $q) {
    return {
      getDashboardData: getDashboardData
    };

    function getDashboardData(params) {

      var params = typeof params !== 'undefined' ? params : {};
      var url = '/subcenter/dashboard/data/';

      if (params.blockid) {
        url = url + params.blockid.toString() + '/';
      }

      if (params.since_months) {
        url = url + '?since_months=' + params.since_months.toString();
      }

      var request = $http({
        method: 'get',
        url: url
      });
      return request.then(handleSuccess, handleError);
    }

    function handleSuccess(response) {
      // return dummy_patient_list
      return response.data;
    }

    function handleError(response) {
      if (!angular.isObject(response.data) || !response.data.message) {
        return ($q.reject('An unknown error occurred.'));
      }
      return $q.reject(response.data.message);
    }
  });

  function DrawPieChart(a, b, c) {
    var data = [{
      data: [
        [1, a]
      ],
      color: '#a0d468'
    }, {
      data: [
        [1, b]
      ],
      color: '#ffce55'
    }, {
      data: [
        [1, c]
      ],
      color: '#fb6e52'
    }];

    var placeholder = $("#dashboard-pie-chart-sources");
    placeholder.unbind();


    $.plot(placeholder, data, {
      series: {
        pie: {
          innerRadius: 0.0,
          show: true,
          stroke: {
            width: 4
          }
        }
      }
    });


    $("#GoodId").text(a);
    $("#AverageId").text(b);
    $("#PoorId").text(c);
  }

  function PoplatePoints(data) {
    var output = new google.maps.LatLng(25.4486, 78.5696);
    var mapOptions = {
      center: output,
      zoom: 9
    };
    var map = new google.maps.Map(document.getElementById('map-canvas'),
      mapOptions);

    for (var i = data.length - 1; i >= 0; i--) {
      var contentString =  '<table style="width:100%">' +
        '<tr>     <td><h5> Subcenter </h5></td> <td> ' + data[i].Subcenter + '</td> </tr>' +
        '<tr>    <td><h5>AshaDetails</h5></td> <td> ' + getAshaDetailString(data[i].AshaDetails) + '</td> </tr>' +
        '<tr>    <td>Beneficiaries</td> <td> ' + data[i].Beneficiaries_anc + data[i].Beneficiaries_pnc + data[i].Beneficiaries_imm + '</td> </tr>' +
        '<tr>    <td>New Registration</td> <td> ' + data[i].new_reg_anc + data[i].new_reg_pnc + data[i].new_reg_pnc + '</td> </tr>' +
        '<tr>    <td>Given Services</td> <td> ' + data[i].GivenServices_anc + data[i].GivenServices_pnc + data[i].GivenServices_imm + '</td> </tr>' +
        '<tr>    <td>Overdue</td> <td> ' + data[i].Overdue_anc + data[i].Overdue_pnc + data[i].Overdue_imm + '</td> </tr>' +
        '<tr>    <td>Overdue Rate</td> <td> ' + ((data[i].OverDueRate_imm + data[i].OverDueRate_pnc + data[i].OverDueRate_anc) / 3).toFixed(2) + '</td> </tr>' +
        '</table>';

      var infowindow = new google.maps.InfoWindow();

      console.log("Print Values" + " " + data[i].lat + " " + data[i].long + " " + data[i].Subcenter);
      var icon_new;
      if (data[i].status == 0) {
        icon_new = "/static/beyond/img/Red.png";
      } else if (data[i].status == 1) {
        icon_new = "/static/beyond/img/Yellow.png";
      } else {
        icon_new = "/static/beyond/img/Green.png";
      }

      var marker = new  MarkerWithLabel({
        position: new google.maps.LatLng(data[i].lat, data[i].long),
        map: map,
        labelContent: data[i].Subcenter,
        labelClass: "my_label", // the CSS class for the label
        labelStyle: {opacity: 0.8},
        labelInBackground: true,
        icon: icon_new
      });

       google.maps.event.addListener(marker, 'click', function_callback(map,marker,contentString,infowindow));
    }
  }
  function function_callback(map,marker,contentString,infowindow)
  {
    return function()
    {
      infowindow.setContent(contentString);
      infowindow.open(map,marker);
    };
  }

  function getAshaDetailString(AshaDetails) {
    var output = "";
    for (var i = 0; i < AshaDetails.length; i++) {
      if (i > 0) {
        output += " ,";
      }
      output += AshaDetails[i];
    }
  }

})();