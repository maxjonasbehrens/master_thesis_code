
# Fit Linear Regression Models to Result Data -----------------------------

# Load Data
library(readr)
result_absolute_country_std <- read_csv("~/Documents/Msc/Thesis/Data/results/result_absolute_country_std.csv")
result_relative_country_std <- read_csv("~/Documents/Msc/Thesis/Data/results/result_relative_country_std.csv")

# Fit LMs to study influence of standard deviation
fit_abs_std <- lm(mae~std, data = result_absolute_country_std)
summary(fit_abs_std)

fit_rel_std <- lm(mae~std, data = result_relative_country_std)
summary(fit_rel_std)

# Fit LMs to study incluence of mean
fit_abs_mean <- lm(mae~mean, data = result_absolute_country_std[-c(14:17),])
summary(fit_abs_mean)

fit_rel_mean <- lm(mae~mean, data = result_relative_country_std)
summary(fit_rel_mean)

# Library to convert LM summary to Latex Table
library(stargazer)
stargazer(fit_abs_mean)
stargazer(fit_rel_mean)

# Both Standard Dev and Mean
fit_rel_all <- lm(mae~std+mean-1, data = result_relative_country_std)
summary(fit_rel_all)

fit_abs_all <- lm(mae~std+mean-1, data = result_absolute_country_std)
summary(fit_abs_all)

# Fit LMs to study influence of N
fit_abs_n <- lm(mae~size, data = result_absolute_country_std)
summary(fit_abs_n)

fit_rel_n <- lm(mae~size, data = result_relative_country_std)
summary(fit_rel_n)

# Visualise
library(dplyr)
library(ggplot2)
library(ggrepel)
library(scales)

# Plot of country level MAE and Country GDP for relative GDP
result_relative_country_std %>% 
  ggplot(aes(mean,mae))+
  geom_label(aes(mean,mae,label=country),position = position_jitter(width = 300,height = 300,seed = 21))+
  xlab("Average GDP per Country (in million €)")+
  ylab("MAE of Predictions on Test Set")+
  scale_x_continuous(labels = comma)+
  scale_y_continuous(labels = comma)+
  ggtitle("")+
  theme_bw(base_size = 16)

ggsave("~/Documents/Msc/Thesis/Data/results/mean_mae_rel.png", height = 6, width = 8)

# Country Level MAE and average Country GDP for Absolute GDP
result_absolute_country_std %>% 
  ggplot(aes(mean,mae))+
  geom_label(aes(mean,mae,label=country),position = position_jitter(width = 2000,height = 300,seed = 272835436))+
  xlab("Average GDP per Country (in million €)")+
  ylab("MAE of Predictions on Test Set")+
  scale_x_continuous(labels = comma)+
  scale_y_continuous(labels = comma)+
  ggtitle("")+
  theme_bw(base_size = 16)

ggsave("~/Documents/Msc/Thesis/Data/results/mean_mae_abs.png", height = 6, width = 8)


# CNN Comparison ----------------------------------------------------------

## NOT USED IN THESIS ##

# Load Data
library(readr)
cnn_results_abs <- read_csv("~/Documents/Msc/Thesis/Data/results/cnn_results_final.csv")
cnn_results_diff <- read_csv("~/Documents/Msc/Thesis/Data/results/cnn_results_diff.csv")

# Plot CNN Prediction accuracy for relative GDP
cnn_results_diff %>% 
  ggplot(aes(val_mse,val_mae,colour=transfer))+
  geom_point()+
  ylim(c(0.25,1))+
  xlim(c(0,5))+
  theme_bw(base_size = 16)+
  xlab("Validation MSE")+
  ylab("Validation MAE")

ggsave("~/Documents/Msc/Thesis/Data/results/diff_models_scatter.png", width = 8, height = 6)

# Plot CNN Prediction accuracy for absolute GDP
cnn_results_abs %>% 
  ggplot(aes(val_mse,val_mae,colour=transfer))+
  geom_point()+
  ylim(c(0.25,1))+
  xlim(c(0,5))+
  theme_bw(base_size = 16)+
  xlab("Validation MSE")+
  ylab("Validation MAE")

ggsave("~/Documents/Msc/Thesis/Data/results/abs_models_scatter.png", width = 8, height = 6)


# CNN Prediction Plot -----------------------------------------------------

# Load data of all predictions
library(readr)
result_preds_abs <- read_csv("~/Documents/Msc/Thesis/Data/results/result_preds_abs.csv")
result_preds_relative <- read_csv("~/Documents/Msc/Thesis/Data/results/result_preds_relative.csv")
enhanced_gdp_data <- read_csv("~/Documents/Msc/Thesis/Data/gdp_data/enhanced_gdp_data.csv")

# Relative GDP - Group by files and take average of predictions
result_preds_relative <- result_preds_relative %>% 
  group_by(test_files, country) %>% 
  summarise_all(mean) %>% 
  mutate(se = (test_true_vals-test_preds)^2, abs_error = abs(test_true_vals-test_preds))

# Relative GDP - Unscaled Accuracy Metrics
mean(result_preds_relative$se)
mean(result_preds_relative$abs_error)

# Absolute GDP - Group by files and take average of predictions
result_preds_abs <- result_preds_abs %>% 
  group_by(test_files, country) %>% 
  summarise_all(mean) %>% 
  mutate(se = (test_true_vals-test_preds)^2, abs_error = abs(test_true_vals-test_preds))

# Absolute GDP - Unscaled Accuracy Metrics
mean(result_preds_abs$se)
mean(result_preds_abs$abs_error)

# Merge absolute and relative results together
result_preds_tot <- merge(result_preds_abs[,c('test_files','test_preds','test_true_vals')],result_preds_relative[,c('test_files','test_preds','test_true_vals')],
                          by='test_files')

# Change column names
names(result_preds_tot) <- c('test_files','abs_preds','true_abs_vals','rel_preds','true_rel_vals')

# Get region and year identifier from file name
library(stringr)
result_preds_tot <- result_preds_tot %>% 
  mutate(nuts2=str_sub(test_files,1,4),year=str_sub(test_files,-8,-5))

# Merge together with true values
result_dat <- merge(result_preds_tot,enhanced_gdp_data[,c("nuts2","year","country_value")],by=c("nuts2","year"))

# Compute Standard Error and bring relative Predictions to same scale
result_dat <- result_dat %>% 
  mutate(rel_pers_preds = country_value+rel_preds) %>% 
  mutate(se = (true_abs_vals-rel_pers_preds)^2)

# Transform results into correct long format
preds_abs <- as_tibble(result_dat[,c('abs_preds','true_abs_vals')])
preds_rel <- as_tibble(result_dat[,c('rel_pers_preds','true_abs_vals')])
names(preds_abs)[1] <- 'test_preds'
names(preds_rel)[1] <- 'test_preds'
preds_abs['pred_metric'] = 'Absolute GDP'
preds_rel['pred_metric'] = 'Relative GDP'

pred <- bind_rows(preds_abs, preds_rel)

# Create Absolute Plots
pred %>% 
  ggplot(aes(test_preds, true_abs_vals, shape=as.factor(pred_metric)))+
  geom_point(size=2)+
  theme_bw(base_size = 16)+
  xlab("Predicted GDP Values (in million €)")+
  ylab("True GDP Values (in million €)")+
  scale_x_continuous(labels = comma)+
  scale_y_continuous(labels = comma)+
  scale_shape_manual(values = c(2,15), name = 'Prediction Metric')

ggsave("~/Documents/Msc/Thesis/Data/results/result_scatter.png", width = 8, height = 6)

# Scaling of True and Predictions Values and transform into long format
scaled.preds_abs <- as_tibble(scale(result_dat[,c('abs_preds','true_abs_vals')]))
scaled.preds_rel <- as_tibble(scale(result_dat[,c('rel_pers_preds','true_abs_vals')]))
names(scaled.preds_abs)[1] <- 'test_preds'
names(scaled.preds_rel)[1] <- 'test_preds'
scaled.preds_abs['pred_metric'] = 'Absolute GDP'
scaled.preds_rel['pred_metric'] = 'Relative GDP'

# Create Scaled Plots
scaled.pred %>% 
  ggplot(aes(test_preds, true_abs_vals, shape=as.factor(pred_metric)))+
  geom_point(size=2)+
  theme_bw(base_size = 16)+
  xlab("Predicted GDP Values")+
  ylab("True GDP Values")+
  scale_x_continuous(labels = comma)+
  scale_y_continuous(labels = comma)+
  scale_shape_manual(values = c(2,15), name = 'Prediction Metric')

ggsave("~/Documents/Msc/Thesis/Data/results/result_scaled_scatter.png", width = 8, height = 6)


