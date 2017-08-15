

# fntltp <- JS("function(){
#              return this.point.x + ' ' +  this.series.yAxis.categories[this.point.y] + ':<br>' +
#              Highcharts.numberFormat(this.point.value, 2);
#              }")
# 
# plotline <- list(
#   color = "#fde725", value = 1963, width = 2, zIndex = 5,
#   label = list(
#     text = "Vaccine Intoduced", verticalAlign = "top",
#     style = list(color = "#606060"), textAlign = "left",
#     rotation = 0, y = -5)
# )
# 
# insider_higchart <- function(){
#   hchart(df %>% filter(format(date, '%d') == '01',
#                        key == 'page_views'), 
#          "heatmap", hcaes(x = date, y = name, value = value)) #%>% 
#   #   hc_colorAxis(stops = color_stops(10, rainbow(10)),
#   #                type = "logarithmic") %>% 
#   #   # hc_yAxis(reversed = TRUE, offset = -20, tickLength = 0,
#   #   #          gridLineWidth = 0, minorGridLineWidth = 0,
#   #   #          labels = list(style = list(fontSize = "8px"))) %>% 
#   #   # hc_tooltip(formatter = fntltp) %>% 
#   #   hc_xAxis(plotLines = list(plotline)) %>%
#   #   hc_title(text = "Infectious Diseases and Vaccines") %>% 
#   #   hc_legend(layout = "vertical", verticalAlign = "top",
#   #             align = "right", valueDecimals = 0)# %>% 
#   # # hc_size(height = 800)
# }


# Define helper for getting cumulative sum of payment amounts
# (base cumsum() doesn't handle NAs the way we want them to)
cum_summer <- function(x){
  x[is.na(x)] <-0
  cumsum(x)
}


# Define functions for generating plots
time_chart <-
  function(data = df,
           the_key = 'page_fan_adds',
           div = 1){
    
    # Define data
    plot_data <- data %>%
      filter(key == the_key) %>%
      group_by(name, date) %>%
      summarise(value_cum = sum(value_cum))
    
    # Define labels
    if(the_key == 'page_views'){
      the_label <- 'Page Views'
    } else if(the_key == 'page_fan_adds'){
      the_label <- 'Fan Adds'
    } else stop('Use only page_views or page_fan_adds for the key')
    
    # Define colors
    cols <- colorRampPalette(brewer.pal(n = 9, name = 'Spectral'))(length(unique(plot_data$name)))
    
    g <- ggplot(data = plot_data,
                aes(x = date,
                    y = value_cum/div,
                    color =  name)) +
      geom_line(size = 1.5) +
      ggtitle(the_label) +
      scale_color_manual(name = '',
                         values = cols) +
      labs(x = 'Date',
           y = paste0('Value ', ' (millions)')) 
    
    return(g)
}

map_city <- function(page) {
  
  if (page == 'all') {
    plot_data <- cities
  } else {
    # get page 
    plot_data <- cities[grepl(page, cities$name),]
  }
 
  page$name <- NULL
  # 
  ggplot() +
    geom_polygon(data = world, aes(x = long, y = lat,
                                   group = group)) +
    geom_point(data = plot_data,
               aes(x = lon,
                   y = lat,
                   size = value),
               col = 'darkorange',
               alpha = 0.6) +
    theme_databrew() +
    theme(legend.position="none") +
    labs(x = '', y = '') +
    ggthemes::theme_map() +
    theme(legend.position = 'none')
}


# charts for comments and likes
simple_chart <- function(page = 'Art',
                         div = 1000000){
  
  if(page == 'all') {
    # get data
    x_sub <- x %>%
      arrange(date) %>%
      filter(date >= dplyr::first(date[value_cum > 0]))
    
    x_sub <- x_sub %>%
      group_by(date, sub_key) %>%
      summarise(mean_cum = mean(value)) %>%
      group_by(sub_key) %>%
      mutate(value_cum = cumsum(mean_cum))
    

  } else {
    # get data
    x_sub <- x %>%
      arrange(date) %>%
      filter(name == page) %>%
      filter(date >= dplyr::first(date[value_cum > 0]))
  }
 
  p <- ggplot(x_sub, aes(date, value_cum/div, colour = sub_key)) +
    geom_line(size = 1.5, alpha = 0.6) +
    xlab('Date') +
    ylab('Value (millions)') +
    ggtitle("2015-2017 Comments and Likes") + 
    theme_databrew() +
    scale_color_manual(values= c('darkorange','blue')) +
    theme(legend.position = 'none')
  p
}

# Functionality for generating fake data
generate_fake_data <- function(df){
  date <- seq(as.Date('2015-01-01'),
              as.Date('2017-08-15'),
              by = 1)
  end_time <- date
  # key <- c('fan_count', 'page_fan_adds', 'page_negative_feedback', 'page_positive_feedback_by_type', 'page_storytellers_by_age_gender', 'page_storytellers_by_city', 'page_storytellers_by_country', 'page_video_views', 'page_views')
  name <- c('Lions Inc.', 'Pictures of monkeys', 'Zebraganza', 'Rhinos 4ever',
            'Giraffes for laughs', 'Armadillo theatre', 'Friends of vampires', 'Videos of cats',
            'Buy/sell stuff', 'Walk the walk', 'Talk the talk', 'Shake and bake', 'Dance in your pants',
            'Board shorts wearers', 'Chevrolet fans', 'Chevrolet haters')
  out <- df
  name_dict <- data.frame(name = sort(unique(df$name)),
                          new_name = sample(name, length(name)))
  # Replace the values
  out <- out %>%
    left_join(name_dict,
              by = 'name') %>%
    dplyr::select(-name) %>%
    mutate(name = new_name) %>%
    dplyr::select(-new_name)
  
  # Change the dates
  out$date <- out$date - 125
  
  # Jitter the values
  out <- out %>%
    mutate(value = jitter(value, factor = 1000)) %>%
    mutate(value = ifelse(value < 0, 0, value)) %>%
    mutate(value = round(value))
  
  # Return the new dataframe
  return(out)
  
}
