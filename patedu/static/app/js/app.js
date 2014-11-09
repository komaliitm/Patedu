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

})();
