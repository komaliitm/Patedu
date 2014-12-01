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

      $scope.dashdata = null;
      fetchDataCurrent();

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