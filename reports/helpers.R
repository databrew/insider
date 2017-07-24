

fntltp <- JS("function(){
             return this.point.x + ' ' +  this.series.yAxis.categories[this.point.y] + ':<br>' +
             Highcharts.numberFormat(this.point.value, 2);
             }")

plotline <- list(
  color = "#fde725", value = 1963, width = 2, zIndex = 5,
  label = list(
    text = "Vaccine Intoduced", verticalAlign = "top",
    style = list(color = "#606060"), textAlign = "left",
    rotation = 0, y = -5)
)

insider_higchart <- function(){
  hchart(df %>% filter(format(date, '%d') == '01',
                       key == 'page_views'), 
         "heatmap", hcaes(x = date, y = name, value = value)) #%>% 
  #   hc_colorAxis(stops = color_stops(10, rainbow(10)),
  #                type = "logarithmic") %>% 
  #   # hc_yAxis(reversed = TRUE, offset = -20, tickLength = 0,
  #   #          gridLineWidth = 0, minorGridLineWidth = 0,
  #   #          labels = list(style = list(fontSize = "8px"))) %>% 
  #   # hc_tooltip(formatter = fntltp) %>% 
  #   hc_xAxis(plotLines = list(plotline)) %>%
  #   hc_title(text = "Infectious Diseases and Vaccines") %>% 
  #   hc_legend(layout = "vertical", verticalAlign = "top",
  #             align = "right", valueDecimals = 0)# %>% 
  # # hc_size(height = 800)
}

# Define helper for getting cumulative sum of payment amounts
# (base cumsum() doesn't handle NAs the way we want them to)
cum_summer <- function(x){
  x[is.na(x)] <-0
  cumsum(x)
}

# Define functions for generating plots
time_chart <-
  function(data = df,
           the_key = 'page_views'){
    
    # Define data
    plot_data <- data %>%
      filter(key == the_key)
    
    # Define labels
    if(the_key == 'page_views'){
      the_label <- 'page views'
    } else if(the_key == 'fan_adds'){
      the_label <- 'fan adds'
    } else stop('Use only page_views or fan_adds for the key')
    
    # Define colors
    cols <- colorRampPalette(brewer.pal(n = 9, name = 'Spectral'))(length(unique(plot_data$name)))
    
    g <- ggplot(data = plot_data,
                aes(x = date,
                    y = value_cum,
                    color =  name)) +
      geom_line() +
      scale_color_manual(name = '',
                         values = cols) +
      guides(color=guide_legend(ncol=4)) +
      labs(x = 'Date',
           y = paste0('Cumulative ', the_label)) 
    
    return(g)
}