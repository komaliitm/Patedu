'use strict';
(function(){
    var app = angular.module('MainApp', [ 'ngRoute', 'infinite-scroll'], function($interpolateProvider) {
      $interpolateProvider.startSymbol('#{');
      $interpolateProvider.endSymbol('}#');
    });

    app.controller('DasboardController', ['$scope', 'dashboardService', function($scope, dashboardService){
      $scope.dashboardParams = {
      	since_months : null,
      	blockid : null
      }

      $scope.dashdata = null;
      fetchDataCurrent();

      function fetchDataCurrent(){
      	dashboardService.getDashboardData($scope.dashboardParams).then(function(dashdata){
        $scope.dashdata = dashdata;
        DrawPieChart($scope.dashdata.summary.Good, $scope.dashdata.summary.Average, $scope.dashdata.summary.Poor);
        console.log($scope.dashdata);
      });	
      }
  	}]);

    app.factory('dashboardService', function($http, $q) {
      return {
        getDashboardData: getDashboardData
      };

      function getDashboardData(params){
      
      	var params = typeof params !== 'undefined' ? params : {};
      	var url = '/subcenter/dashboard/data/';

      	if(params.blockid)
      	{
      		url = url + params.blockid.toString() + '/';
      	}

      	if(params.since_months)
      	{
      		url = url + '?since_months='+params.since_months.toString();
      	}

        var request = $http({
          method: 'get',
          url: url
        });
        return request.then(handleSuccess, handleError);
      }

      function handleSuccess(response){
        // return dummy_patient_list
        return response.data;
      }

      function handleError(response) {
        if (!angular.isObject(response.data) || !response.data.message) {
          return ($q.reject( 'An unknown error occurred.' ));
        }
        return $q.reject(response.data.message);
      }
    });


    function DrawPieChart(a, b, c) 
    {
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

})();