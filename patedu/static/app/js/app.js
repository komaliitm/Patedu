'use strict';
(function() {
  var app = angular.module('MainApp', ['ngRoute'], function($interpolateProvider) {
    $interpolateProvider.startSymbol('#{');
    $interpolateProvider.endSymbol('}#');
  });

app.directive('onFinishRender', function ($timeout) {
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            if (scope.$last === true) {
                $timeout(function () {
                    scope.$emit('ngRepeatFinished');
                });
            }
        }
    }
  });

  app.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
      // route for the Main page
      .when('/subcenter/', {
        templateUrl : 'subcenter_report/',
        controller  : 'SubcenterController'
      })
      // route for the template page
      .when('/block/', {
        templateUrl : 'block_report/',
        controller  : 'BlockController'
      })
      // route for the outreach page
      .when('/outreach/', {
        templateUrl : 'outreach_monitoring_report/',
        controller  : 'OutreachController'
      })
      .otherwise({
              redirectTo: '/subcenter/'
      });
    }]);


  app.controller('MainController', ['$scope', '$location', function($scope, $location){
    console.log("In Main controller");
    $scope.isActive = function (route) {
      return $location.path().indexOf(route) === 0;
      // return route === $location.path();
    };
  }]);

  app.controller('BlockController', ['$scope', 'blockService', function($scope, blockService){
    console.log("In Block controller");
    var InitiateHorizonalChart = function (elem, my_data, tickLabels) {
      return {
              init: function () {
                  // // Set up our data array  
                  // var my_data = [[50, 0], [95, 1], [60, 2], [90, 3], [65, 4], [85, 5], [70, 6], [80, 7]];
                  // // Setup labels for use on the Y-axis  
                  // var tickLabels = [[0, 'Badagaon'], [1, 'Gursarai'], [2, 'Bamaur'], [3, 'Babina'], [4, 'Chirgaon'], [5, 'Bangra'], [6, 'Mauranipur'], [7, 'Moth']];
                  $.plot($(elem), [
                  {
                      data: my_data,
                      bars: {
                          show: true,
                          align: 'center',
                          horizontal: true
                      }
                  }
                  ],
                  {
                      bars: {
                          fillColor: { colors: [{ opacity: 0.8 }, { opacity: 1 }] },
                          barWidth: 0.50,
                          lineWidth: 1.0,
                          borderWidth: 0
                      },
                      colors: [themeprimary],
                      yaxis: {
                          ticks: tickLabels
                      },
                      grid: {
                          show: true,
                          hoverable: true,
                          clickable: true,
                          tickColor: gridbordercolor,
                          borderWidth: 0,
                          borderColor: gridbordercolor,
                      },
                  }
                  );
              }
          };
      };
      var InitiateEasyPieChart = function (elem) {
          return {
              init: function () {
                  var easypiecharts = $(elem);
                  $.each(easypiecharts, function () {
                      var barColor = getcolor($(this).data('barcolor')) || themeprimary,
                          trackColor = getcolor($(this).data('trackcolor')) || false,
                          scaleColor = getcolor($(this).data('scalecolor')) || false,
                          lineCap = $(this).data('linecap') || "round",
                          lineWidth = $(this).data('linewidth') || 3,
                          size = $(this).data('size') || 110,
                          animate = $(this).data('animate') || false;

                      $(this).easyPieChart({
                          barColor: barColor,
                          trackColor: trackColor,
                          scaleColor: scaleColor,
                          lineCap: lineCap,
                          lineWidth: lineWidth,
                          size: size,
                          animate : animate
                      });
                  });
              }
          };
      };

      var setupHorizonalCharts = function()
      {
        angular.forEach($scope.block_indices.block_graph_data, function(graph_data, pillar){
          InitiateHorizonalChart($('#'+pillar), graph_data[0], graph_data[1]).init();
        });
      }

      $scope.block_indices = null;

      var RefreshBlockData = function()
      {
        $('.loading-container').removeClass('loading-inactive');
        blockService.getBlockIndicesData('36').then( function(block_indices){
          $scope.block_indices = block_indices;
          setupHorizonalCharts();
          $('.loading-container').addClass('loading-inactive');

          $scope.$watch(function (scope) {
              return scope.block_indices.district_data.del_rep.percent;
            },
            function (newValue, oldValue) {
              InitiateEasyPieChart($('#doughnut-drep')).init();
            }
          );

          $scope.$watch(function (scope) {
              return scope.block_indices.district_data.child_reg.percent;
            },
            function (newValue, oldValue) {
              InitiateEasyPieChart($('#doughnut-child-reg')).init();
            }
          );

          $scope.$watch(function (scope) {
              return scope.block_indices.district_data.mother_reg.percent;
            },
            function (newValue, oldValue) {
              InitiateEasyPieChart($('#doughnut-mother-reg')).init();
            }
          );

          $scope.$watch(function (scope) {
              return scope.block_indices.district_data.full_anc.percent;
            },
            function (newValue, oldValue) {
              InitiateEasyPieChart($('#doughnut-fanc')).init();
            }
          );

          $scope.$watch(function (scope) {
              return scope.block_indices.district_data.full_imm.percent;
            },
            function (newValue, oldValue) {
              InitiateEasyPieChart($('#doughnut-fimm')).init();
            }
          );


        }, function(error){
          $('.loading-container').addClass('loading-inactive');
          alert('Unknown error. Please try after sometime.')
        });
      }

      //End Init Section
      RefreshBlockData();
  }]);

  app.controller('OutreachController', ['$scope', 'outreachService', 
    function($scope, outreachService){
    $scope.outreach = {};
    var RefreshOutreachData = function(){
      $('.loading-container').removeClass('loading-inactive');
      outreachService.getOutreachData('36', 0).then( function(outreach){
        $scope.outreach = outreach;
        $('.loading-container').addClass('loading-inactive');
      }, function(error){
        $('.loading-container').addClass('loading-inactive');
        alert('Unknown error. Please try after sometime.')
      });
    }
    RefreshOutreachData();
    console.log("In Outreach controller");
  }]);

  app.controller('SubcenterController', ['$scope', 'subcenterService',
    function($scope, subcenterService) {
      $scope.dashboardParams = {
        since_months: 1,
        blockid: "",
        domain: "1"
      }

      $scope.RefreshDataFromServer = function($event, type){
        fetchDataCurrent();
      }
      $scope.Asc =0; 
      $scope.SerialNum=0;
      $scope.loading = false;
      $scope.Completeloading = true;
      $scope.dashdata = null;
      $scope.currentWP = {}; 
      fetchDataCurrent();

      $scope.$watch(function (scope) {
          return scope.dashboardParams.domain;
        },
        function (newValue, oldValue) {
          $scope.SerialNum = 0;
        }
      );
       
      $scope.PrintElem = function (elem)
      {
          Popup($(elem).html());
      }

      var Popup = function(data) 
      {
          var mywindow = window.open('', 'my div', 'height=400,width=600');
          mywindow.document.write('<html><head><title>my div</title>');
          mywindow.document.write('<link rel="stylesheet" href="/static/beyond/css/bootstrap.min.css" type="text/css" />');
          mywindow.document.write('<link rel="stylesheet" href="/static/beyond/css/font-awesome.min.css" type="text/css" />');
          mywindow.document.write('<link rel="stylesheet" href="/static/beyond/css/beyond.min.css" type="text/css" />');
          mywindow.document.write('<link rel="stylesheet" href="/static/app/css/dashboard_subcenterblock.css" type="text/css" />');
          mywindow.document.write('</head><body >');
          mywindow.document.write(data);
          mywindow.document.write('</body></html>');

          mywindow.document.close(); // necessary for IE >= 10
          mywindow.focus(); // necessary for IE >= 10

          mywindow.print();
          mywindow.close();

          return true;
      }

      $scope.SortData = function($event, type) {
          //Sort the dashdata according to type
          if($scope.SerialNum == type)
          {
              $scope.Asc > 0 ? $scope.Asc =0 : $scope.Asc =1;
          }
          else
            $scope.Asc =0;

          var context = $scope.dashboardParams.domain;

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
                  keyA = context=='1'?a.Beneficiaries_anc:a.Beneficiaries_imm;
                  keyB = context=='1'?b.Beneficiaries_anc:b.Beneficiaries_imm;
              }
              else if (type == 4) {
                  keyA = context=='1'?a.DueServices_anc:a.DueServices_imm;
                  keyB = context=='1'?b.DueServices_anc:b.DueServices_imm;
              }
              else if (type == 5) {
                  keyA = context=='1'?a.GivenServices_anc:a.GivenServices_imm;
                  keyB = context=='1'?b.GivenServices_anc:b.GivenServices_imm;
              }
              else if (type == 6) {
                  keyA = context=='1'?a.Overdue_anc:a.Overdue_imm;
                  keyB = context=='1'?b.Overdue_anc:b.Overdue_imm;
              }
              else {
                  keyA = context=='1'?a.OverDueRate_anc:a.OverDueRate_imm;
                  keyB = context=='1'?b.OverDueRate_anc:b.OverDueRate_imm;
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

      $scope.WorkplanModal = function(subc_id)
      {
        var mode = 'ANC';
        if($scope.dashboardParams.domain == '2')
        {
          mode = 'IMM';
        }

        //Get Workplan data for current subcenter
        $scope.loading = true;
        $scope.Completeloading = false;
        $('.loading-container').removeClass('loading-inactive');
        subcenterService.getWorkplanData(subc_id, mode, $scope.dashboardParams.since_months).then( function(wpData){
          $scope.currentWP = wpData;
          $scope.loading = false;
          $scope.Completeloading = true;
          $('.loading-container').addClass('loading-inactive');
          $('#workplan_modal').modal({show:'true'});
        }, function(error){
          $scope.loading = false;
          $scope.Completeloading = true;
          $('.loading-container').addClass('loading-inactive');
          alert('Unknown error. Please try after sometime.')
        });

        return;
      } 
           
      var initSparkLines = function() {
        console.log("Init Spark Lines")
        for(var i=0;i<$scope.dashdata.data.length;i++)
        {
          SparkLineInit('sparkline-anc-'+i, $scope.dashdata.data[i].ProgressData_anc);
          SparkLineInit('sparkline-imm-'+i,$scope.dashdata.data[i].ProgressData_imm);
        }
      }

      $scope.$on('ngRepeatFinished', function(ngRepeatFinishedEvent) {
            initSparkLines();
            initToolTips();
      });

      var initToolTips = function(){
        $('[data-toggle="popover"]').popover();
      }

      var SparkLineInit = function(spark_line_id, data){
              var sparklinelines =  $('#'+spark_line_id);
              $.each(sparklinelines, function () {
                  $(this).sparkline(data, {
                      type: 'line',
                      disableHiddenCheck: true,
                      height: $(this).data('height'),
                      width: $(this).data('width'),
                      fillColor: getcolor($(this).data('fillcolor')),
                      lineColor: getcolor($(this).data('linecolor')),
                      spotRadius: $(this).data('spotradius'),
                      lineWidth: $(this).data('linewidth'),
                      spotColor: getcolor($(this).data('spotcolor')),
                      highlightLineColor: getcolor($(this).data('highlightlinecolor')),
                      chartRangeMin: 0,
                      chartRangeMax: 10
                  });
              });
        }


        function fetchDataCurrent() {
          $scope.loading = true;
          $scope.Completeloading = false;
          $('.loading-container').removeClass('loading-inactive');

           subcenterService.getDashboardData($scope.dashboardParams).then(function(dashdata) {
            $scope.dashdata = dashdata;
            DrawPieChart($scope.dashdata.summary.Good, $scope.dashdata.summary.Average, $scope.dashdata.summary.Poor);
            PoplatePoints($scope.dashdata.data);
            console.log($scope.dashdata);
            $scope.loading = false;
            $scope.Completeloading = true;
            $('.loading-container').addClass('loading-inactive');
          }, function(error){
              $scope.Completeloading = true;
              $scope.loading = false;
              $('.loading-container').addClass('loading-inactive');
              if($.isNumeric(error) && error==405)
              {
                alert('Data is getting loaded. Please try again after 10 mins.');
              }
              else if(!$.isNumeric(error)){
                alert(error);
              }
              else{
               alert('Unknown error occured. Please try again later.'); 
              }
            }
          );
        }
      }
  ]);

      
  app.filter('services_dump', function () {
    return function (service_maps) {
        var dump = '';
        angular.forEach(service_maps, function(service_map){
          if(dump)
          {
            dump += ', '
          }
          dump += service_map.event_name+':'+service_map.ods_count
        });
        return dump;
    };
  });

  app.filter('gs_map', function () {
    return function (d_services) {
        var dump = '';
        angular.forEach(d_services, function(d_service){
          if(dump)
          {
            dump += ', '
          }
          dump += d_service.event.val
        });
        return dump;
    };
  });

  app.filter('d_map', function () {
    return function (d_services) {
        var dump = '';
        angular.forEach(d_services, function(d_service){
          if(dump)
          {
            dump += ', '
          }
          var d_split = new Date(d_service.timestamp).toString().split(' ')
          var d_val = d_split[1]+' '+d_split[3]
          dump += d_service.event.val+' ('+d_val+')'
        });
        return dump;
    };
  });

  app.filter('wp_duration', function () {
    return function (date_this, date_then) {
        var dt_this = new Date(date_this);
        var dt_then = new Date(date_then);
        var d_split_this = dt_this.toString().split(' ');
        var d_split_then = dt_then.toString().split(' ');
        if(dt_this.toDateString() == dt_then.toDateString())
        { 
            return d_split_this[1]+', '+d_split_this[3];
        }

        return  d_split_then[1]+', '+d_split_then[3]+" to "+d_split_this[1]+', '+d_split_this[3];
    };
  });

  app.factory('outreachService', function($http, $q){
    return {
      getOutreachData: getOutreachData
    };

    function getOutreachData(district_id, months_back){
      var url = '/subcenter/dashboard/outreach/data/';
      
      url += '?district_id='+district_id+'&'+'months_back='+months_back; 

      var request = $http({
        method:'get',
        url:url
      });
      return request.then(handleSuccess, handleError);
    }

    function handleSuccess(response) {
      return response.data;
    }

    function handleError(response) {
      if (!angular.isObject(response.data) || !response.data.message) {
        return ($q.reject(response.status) );
      }
      return $q.reject(response.data.message);
    }

  });  

  app.factory('blockService', function($http, $q){
    return {
      getBlockIndicesData: getBlockIndicesData
    };

    function getBlockIndicesData(district_id){
      var url = '/subcenter/dashboard/block_report/data/';
      if(district_id)
      {
        url += '?district_id='+district_id; 
      }

      var request = $http({
        method:'get',
        url:url
      });
      return request.then(handleSuccess, handleError);
    }

    function handleSuccess(response) {
      // return dummy_patient_list
      return response.data;
    }

    function handleError(response) {
      if (!angular.isObject(response.data) || !response.data.message) {
        return ($q.reject(response.status) );
      }
      return $q.reject(response.data.message);
    }

  });

  app.factory('subcenterService', function($http, $q) {
    return {
      getDashboardData: getDashboardData,
      getWorkplanData:getWorkplanData
    };

    function getWorkplanData(subc_id, mode, since_months)
    {
      var url = '/subcenter/dashboard/workplan/';
      url = url + '?subc_id='+subc_id+'&report_type='+mode+'&since_months='+since_months;
      
      var request = $http({
        method: 'get',
        url: url
      });
      return request.then(handleSuccess, handleError);      
    }

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
        return ($q.reject(response.status) );
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
      zoom: 11
    };
    var map = new google.maps.Map(document.getElementById('map-canvas'),
      mapOptions);

    for (var i = data.length - 1; i >= 0; i--) {
      var x = data[i].Beneficiaries_anc + data[i].Beneficiaries_pnc + data[i].Beneficiaries_imm;
      var x2 = data[i].new_reg_anc + data[i].new_reg_pnc + data[i].new_reg_pnc;
      var x3 = data[i].GivenServices_anc + data[i].GivenServices_pnc + data[i].GivenServices_imm;
      var x4 = data[i].Overdue_anc + data[i].Overdue_pnc + data[i].Overdue_imm;
      var x5 = ((data[i].OverDueRate_imm + data[i].OverDueRate_pnc + data[i].OverDueRate_anc) / 2).toFixed(2);
            
      var contentString =  '<table style="width:100%">' +
        '<tr>     <td><h5> Subcenter </h5></td> <td> ' + data[i].Subcenter + '</td> </tr>' +
        '<tr>    <td><h5>ANMDetails</h5></td> <td> ' + getAshaDetailString(data[i].ANMDetails) + '</td> </tr>' +
        '<tr>    <td><h5>AshaDetails</h5></td> <td> ' + getAshaDetailString(data[i].AshaDetails) + '</td> </tr>' +
        '<tr>    <td>Beneficiaries</td> <td> ' + x + '</td> </tr>' +
        '<tr>    <td>New Registration</td> <td> ' + x2 + '</td> </tr>' +
        '<tr>    <td>Given Services</td> <td> ' + x3 + '</td> </tr>' +
        '<tr>    <td>Overdue</td> <td> ' + x4 + '</td> </tr>' +
        '<tr>    <td>Overdue Rate</td> <td> ' + x5 + '</td> </tr>' +
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
    return output;
  }

})();