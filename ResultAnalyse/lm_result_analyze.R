
# Fit Linear Regression Models to Result Data -----------------------------

# Load Data

library(readr)
result_absolute_country_std <- read_csv("~/Documents/Msc/Thesis/Data/results/result_absolute_country_std.csv")
result_relative_country_std <- read_csv("~/Documents/Msc/Thesis/Data/results/result_relative_country_std.csv")

# Fit LMs to study influence of standard deviation
fit_abs_std <- lm(mse~std, data = result_absolute_country_std)
summary(fit_abs_std)

fit_rel_std <- lm(mse~std, data = result_relative_country_std)
summary(fit_rel_std)

# Fit LMs to study incluence of mean
fit_abs_mean <- lm(mae~mean, data = result_absolute_country_std[-c(14:17),])
summary(fit_abs_mean)

fit_rel_mean <- lm(mae~mean, data = result_relative_country_std)
summary(fit_rel_mean)

library(stargazer)

stargazer(fit_abs_mean)
stargazer(fit_rel_mean)

# Both
fit_rel_all <- lm(mse~std+mean-1, data = result_relative_country_std)
summary(fit_rel_all)

fit_abs_all <- lm(mse~std+mean-1, data = result_absolute_country_std)
summary(fit_abs_all)

# Fit LMs to study influence of N
fit_abs_n <- lm(mse~size, data = result_absolute_country_std)
summary(fit_abs_n)

fit_rel_n <- lm(mse~size, data = result_relative_country_std)
summary(fit_rel_n)

# Visualise
library(dplyr)
library(ggplot2)
library(ggrepel)

result_relative_country_std %>% 
  ggplot(aes(mean,mae))+
  geom_label(aes(mean,mae,label=country),position = position_jitter(width = 300,height = 300,seed = 24))+
  xlab("Mean GDP per Country")+
  ylab("MAE of Predictions on Test Set")+
  ggtitle("")+
  theme_bw(base_size = 16)

result_relative_country_std %>% 
  ggplot(aes(mean,mse))+
  geom_label(aes(mean,mse,label=country),position = position_jitter(width = 300,height = 6000000,seed=69))+
  xlab("Mean GDP per Country")+
  ylab("MSE of Predictions on Test Set")+
  ggtitle("")+
  theme_bw(base_size = 16)

ggsave("~/Documents/Msc/Thesis/Data/results/mean_mse_rel.png", height = 6, width = 8)

result_absolute_country_std %>% 
  ggplot(aes(mean,mae))+
  geom_label(aes(mean,mae,label=country),position = position_jitter(width = 500,height = 500,seed = 12))+
  xlab("Mean GDP per Country")+
  ylab("MAE of Predictions on Test Set")+
  ggtitle("")+
  theme_bw(base_size = 16)

ggsave("~/Documents/Msc/Thesis/Data/results/mean_mse_abs.png", height = 6, width = 8)
